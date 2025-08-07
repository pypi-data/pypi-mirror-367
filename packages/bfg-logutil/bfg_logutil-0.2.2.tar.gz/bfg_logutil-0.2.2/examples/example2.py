from logutil import log, logctx

with logctx(a=123):
    log.info("hello", b=100)

with logctx(x=1):
    with logctx(y=2):
        with logctx(y=100):  # overwrite y
            log.info("hello", z=3)
