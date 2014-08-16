import Queue
import threading


class ThreadingManager(object):
    """
    class that manage multiple threads
    """

    def __init__(self):
        self.queue = Queue.Queue()
        self.threads_list = []
        self.thread_name_counter = 0

    def start_task(self, target_func, name, para):
        """
        Function to create and start a single new threads with input
        parameters, which includes a synchronised queue to store results from the
        threads if there are any.

        :param target_func: The content of the thread
        :param name:        Name the the thread
        :param para:        Input parameter of threads
        :return The newly started thread
        """

        # pass queue to the worker function by default
        para += (self.queue,)

        new_thread = threading.Thread(
            target=target_func,
            name=name+str(name),
            args=para
        )

        new_thread.start()
        self.threads_list.append(new_thread)

        return new_thread

    def start_tasks(self, target_func, name, para):
        """
        Function to create and start new threads with input parameters, which
        includes a synchronised queue to store results from threads if there
        are any. Threads are stored in the threads list for management purposes

        :param target_func: The content of the thread
        :param name:        Name the the thread
        :param para:        Input parameter of threads
        """

        # pass queue to the worker function by default
        para += (self.queue,)

        new_thread = threading.Thread(
            target=target_func,
            name=name+str(self.thread_name_counter),
            args=para
        )

        new_thread.start()
        self.threads_list.append(new_thread)
        self.thread_name_counter += 1

    def collect_results(self):
        """
        Wait for all threads to finish. Results should be written to the queue
        if there are any results

        :return: The queue that stores results
        """
        for thread in self.threads_list:
            thread.join()

        return self.queue