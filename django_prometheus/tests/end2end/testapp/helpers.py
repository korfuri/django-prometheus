DJANGO_MIDDLEWARES = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
]


def get_middleware(before, after):
    middleware = [before]
    middleware.extend(DJANGO_MIDDLEWARES)
    middleware.append(after)
    return middleware
