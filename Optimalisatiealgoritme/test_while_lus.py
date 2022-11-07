import time
while 1 == 1:
    import test1
    from test1 import sentinel
    while sentinel == 1:
        print('in loop')
        time.sleep(2)
        import test1
    if sentinel == 0:
        time.sleep(2)
        print(2)
        import test1
