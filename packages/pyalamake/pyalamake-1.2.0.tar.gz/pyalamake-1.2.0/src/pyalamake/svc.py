# --------------------
## holds singletons and global values
class svc:  # pylint: disable=invalid-name
    ## holds reference to logger
    log = None

    ## holds global information
    gbl = None

    ## holds OS Abstraction Layer
    osal = None

    # --------------------
    ## abort the current script.
    # Note: do not use logging here since it may fail to write correctly
    #
    # @param msg  (optional) message to display
    # @return does not return
    @classmethod
    def abort(cls, msg='abort occurred, exiting'):
        if svc.log:
            svc.log.save()
        import sys
        print('')
        print(f'ABRT {msg}')
        sys.stdout.flush()
        sys.exit(1)
