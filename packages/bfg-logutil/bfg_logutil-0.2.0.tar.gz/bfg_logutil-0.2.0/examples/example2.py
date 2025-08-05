from logutil import log, logctx

with logctx(a=123):
    log.info("hello", b=100)
