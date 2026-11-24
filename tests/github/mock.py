"""Fake Supabase (auth + the two tables) for Playwright tests: route every request to the project URL here."""
import json, time, re, uuid
from urllib.parse import urlparse, parse_qs
class Mock:
    def __init__(self, teachers=()):
        self.users = {}; self.codes = {}; self.rows = {}; self.teachers = set(teachers); self.log = []; self.down = False
    def uid(self, req):
        a = req.headers.get("authorization", "")
        m = re.match(r"Bearer tok-(.+)", a); return m.group(1) if m else None
    def email_of(self, uid): return next(e for e, u in self.users.items() if u["id"] == uid)
    def sess(self, email):
        u = self.users[email]; return {"access_token": "tok-" + u["id"], "refresh_token": "rt-" + u["id"], "expires_in": 3600, "expires_at": int(time.time()) + 3600, "user": {"id": u["id"], "email": email}}
    async def handle(self, route):
        req = route.request; url = urlparse(req.url); q = parse_qs(url.query); path = url.path
        body = json.loads(req.post_data) if req.post_data else {}
        self.log.append((req.method, path, url.query))
        def send(st, obj): return route.fulfill(status=st, content_type="application/json", body=json.dumps(obj), headers={"access-control-allow-origin": "*"})
        if self.down: return await route.abort()
        if req.method == "OPTIONS": return await route.fulfill(status=200, headers={"access-control-allow-origin": "*", "access-control-allow-headers": "*", "access-control-allow-methods": "*"})
        if path == "/auth/v1/otp":
            e = body["email"]
            if not (e.endswith("@schools.vic.edu.au") or e.endswith("@education.vic.gov.au") or e in self.teachers):
                return await send(500, {"code": 500, "error_code": "unexpected_failure", "msg": "Database error saving new user"})
            self.users.setdefault(e, {"id": str(uuid.uuid4()), "pw": None}); self.codes[e] = "123456"; return await send(200, {})
        if path == "/auth/v1/verify":
            e = body["email"]
            if self.codes.get(e) != body["token"]: return await send(403, {"code": 403, "error_code": "otp_expired", "msg": "Token has expired or is invalid"})
            return await send(200, self.sess(e))
        if path == "/auth/v1/user" and req.method == "PUT":
            u = self.uid(req); e = self.email_of(u); self.users[e]["pw"] = body["password"]; return await send(200, {"id": u, "email": e})
        if path == "/auth/v1/token":
            if q["grant_type"][0] == "password":
                e = body["email"]; u = self.users.get(e)
                if not u or u["pw"] != body["password"]: return await send(400, {"code": 400, "error_code": "invalid_credentials", "msg": "Invalid login credentials"})
                return await send(200, self.sess(e))
            uid = body["refresh_token"][3:]; return await send(200, self.sess(self.email_of(uid)))
        if path == "/auth/v1/logout": return await send(204, {})
        u = self.uid(req)
        if not u: return await send(401, {"message": "JWT expired"})
        if not any(x["id"] == u for x in self.users.values()):
            if path == "/auth/v1/user": return await send(403, {"code": 403, "error_code": "user_not_found", "msg": "User from sub claim in JWT does not exist"})
            if req.method == "POST": return await send(409, {"code": "23503", "message": 'insert or update on table "progress" violates foreign key constraint'})
            return await send(200, [])
        if path == "/auth/v1/user" and req.method == "GET": return await send(200, {"id": u})
        me = self.email_of(u); teacher = me in self.teachers
        if path.startswith("/rest/v1/rpc/"):
            fn = path.split("/")[-1]
            if not teacher: return await send(400, {"message": "Teachers only"})
            if fn == "teacher_list_students": return await send(200, [{"email": e, "created_at": "x", "last_sign_in_at": None} for e in self.users if e.endswith("@schools.vic.edu.au") or e.endswith("@tt50.example.com")])
            e = body["student_email"].lower()
            if not (e.endswith("@schools.vic.edu.au") or e.endswith("@education.vic.gov.au") or e.endswith("@tt50.example.com")): return await send(200, "not a school email")
            if fn == "teacher_add_student":
                if e in self.users: return await send(200, "exists")
                self.users[e] = {"id": str(uuid.uuid4()), "pw": body["student_password"]}; return await send(200, "created")
            if fn == "teacher_delete_student":
                if e not in self.users: return await send(200, "no account")
                uid = self.users.pop(e)["id"]; self.rows.pop(uid, None); return await send(200, "deleted")
            if fn == "teacher_set_password":
                if e not in self.users: return await send(200, "no account")
                self.users[e]["pw"] = body["student_password"]; return await send(200, "done")
        if path == "/rest/v1/teachers": return await send(200, [{"email": me}] if teacher else [])
        if path == "/rest/v1/progress":
            if req.method == "GET":
                want = q.get("user_id", [None])[0]
                rows = [r for r in self.rows.values() if teacher or r["user_id"] == u]
                if want: rows = [r for r in rows if r["user_id"] == want[3:]]
                return await send(200, rows)
            if body["user_id"] != u: return await send(403, {"message": "RLS"})
            r = {"user_id": u, "email": me, "name": body.get("name"), "data": body["data"], "updated_at": "2026-11-20T%02d:%02d:%02d.%06dZ" % (time.gmtime()[3], time.gmtime()[4], time.gmtime()[5], int(time.time()*1e6) % 1000000)}
            self.rows[u] = r; return await send(201, [{"updated_at": r["updated_at"]}])
        return await send(404, {"message": "no route " + path})
