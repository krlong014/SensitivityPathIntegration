from mpi4py import MPI
from collections import deque
import logging


class Boss:

    def __init__(self, taskInputs, analyzer, comm=MPI.COMM_WORLD,
            logLevel=logging.INFO):

        self.comm = comm
        self.taskArgList = taskInputs
        self.analyzer = analyzer
        logging.basicConfig(format='[Boss] %(message)s',
            level=logLevel)

    def loop(self):

        # Get information about the multiprocessor environment
        comm = self.comm
        rank = comm.Get_rank()
        nProcs = comm.Get_size()

        # Form a queue of the arguments to be sent
        taskQ = deque(self.taskArgList)

        # Form a queue of the available worker processors
        availableWorkers = deque(range(1,nProcs))

        # Set up arrays in which to store information about pending
        # messages from the workers
        pendingReplies = []
        replySources = []

        # Main loop: continue until all task queue is empty and
        # all pending responses have been processed.
        while len(taskQ) > 0 or len(pendingReplies)>0:

            # If a worker is available, send it a task
            if len(availableWorkers) > 0 and len(taskQ)>0:
                workerRank = availableWorkers.popleft()
                taskArg = taskQ.popleft()

                # Send the task request
                logging.debug('sending args {} to worker {}'
                    .format(taskArg, workerRank))
                comm.isend( ('TASK', taskArg), dest=workerRank, tag=1)

                # Open a receiver for the results
                reply = comm.irecv(source=workerRank, tag=2)
                pendingReplies.append(reply)
                replySources.append(workerRank)

            # Check for replies from busy workers
            (index, hasResult, result) = MPI.Request.testany(pendingReplies)
            if hasResult:
                # Look up who sent the reply
                reply = pendingReplies[index]
                workerRank = replySources[index]
                logging.debug('got msg=[{}] from worker [{}]'
                    .format(result, workerRank))

                # Send the result to the analyzer
                self.analyzer.acceptResult(result)

                # Clear the reply out of the pending list
                pendingReplies.remove(reply)
                replySources.remove(workerRank)

                # Mark the worker processor as available again
                logging.debug('Putting worker [{}] back on queue'
                    .format(workerRank))
                if len(taskQ)>0:
                    availableWorkers.append(workerRank)

        # End of main loop, all tasks finished. Send shutdown messages
        # to all workers
        for p in range(1,nProcs):
            logging.debug('Sending shutdown message to worker [{}]'.format(p))
            comm.isend( ('DONE',), dest=p, tag=1)

        # All done!
        logging.debug('Boss shutting down')
