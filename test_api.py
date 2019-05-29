import unittest
import multiprocessing
import threading
import random
import time

from api import retrive_post

class TestApi(unittest.TestCase):

    def test_multiple_process_access(self):
        pool = multiprocessing.Pool(processes=5)

        results = []

        for post_id in range(1, 65):
            time.sleep(random.uniform(0.1, 0.5))
            async_result = pool.apply_async(retrive_post, args=(post_id, ))
            results.append((post_id,  async_result))

        [result[1].wait() for result in results]

        for result in results:
            post_id, async_result = result
            
            try:
                print(f'{async_result.get()}')
            except Exception as exp:
                if hasattr(exp, 'status_code') and exp.status_code == 1:
                    print(f'{post_id}: proxies are hot')
                else:
                    print(exp)

    def catch_thread_exception(self, func):
        def wrapper(post_id):
            try:
                return True, post_id, func(post_id)
            except Exception as exp:
                return False, post_id, exp
        
        return wrapper

    def test_multiple_threads_access(self):
        queue = multiprocessing.Queue()
        threads = []

        for post_id in range(1, 62):
            time.sleep(random.uniform(0.1, 0.5))
            thread = threading.Thread(target=lambda queue, post_id: queue.put(self.catch_thread_exception(retrive_post)(post_id)), args=(queue, post_id,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        while not queue.empty():
            is_successful, post_id, result = queue.get()

            if is_successful:
                print(f'{result}')
            else:
                if hasattr(result, 'status_code') and result.status_code == 1:
                    print(f'{post_id}: proxies are hot')
                else:
                    print(result)


if __name__ == '__main__':
    unittest.main()
