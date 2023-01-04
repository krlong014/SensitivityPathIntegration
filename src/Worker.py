from mpi4py import MPI
import logging


class Worker:

    def __init__(self, func, comm=MPI.COMM_WORLD, logLevel=logging.INFO):
        self.comm = comm
        self.func = func
        logging.basicConfig(format='[Worker rank={}] %(message)s'
            .format(self.comm.Get_rank()), level=logLevel)

    def loop(self):

        rank = self.comm.Get_rank()

        while True:
            # Wait for incoming message
            logging.debug('Worker [{}] waiting'.format(rank))
            request = self.comm.irecv(source=0, tag=1)
            msg = request.wait()

            if msg[0]=='DONE': # Shutdown notice
                logging.debug('Worker [{}] shutting down'.format(rank))
                break
            elif msg[0]=='TASK': # Task request
                # Unpack the request
                arg = msg[1]
                logging.debug('starting task with arg=[{}]'.format(arg))
                # Do the work
                result = self.func.run(arg)
                logging.debug('finished task')
                # Send results back to the manager
                self.comm.isend(result, dest=0, tag=2)
            else:
                logging.error('Unknown message {}'.format(msg))
