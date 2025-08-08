from .Solution import Solution

class Solution_135(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 135, 'Hard')

    main = None

    def candy(self, ratings):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/candy/?envType=daily-question&envId=2025-06-02

        :type ratings: List[int]
        :rtype: int
        '''

        n = len(ratings)
        candy = [1] * n

        for i in range(1, n):
            if ratings[i] > ratings[i - 1]:
                if candy[i] <= candy[i - 1]:
                    candy[i] = candy[i - 1] + 1 # in cases like 1, 2, 3 where they are in a row

        for i in reversed(range(n - 1)):
            if ratings[i] > ratings[i + 1]:
                if candy[i] <= candy[i + 1]:
                    candy[i] = max(candy[i], candy[i + 1]) + 1 # if this one is equal to the other or the other is greater than this

        return sum(candy)

    main = candy

class Solution_440(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 440, 'Hard')

    main = None

    def findKthNumber(self, n, k):
        '''
        Plan: if the we can go from 1 - 2, 11 - 12, do it. If we cannot, then go from 1 - 10, 11 - 110.
        Either next lexicographical sibling or child.
        '''

        '''
        Author: Kevin zhu
        Link: https://leetcode.com/problems/k-th-smallest-in-lexicographical-order/?envType=daily-question&envId=2025-06-09

        :type k: int
        :rtype: int
        '''

        def count_between(n, f):
            steps = 0
            l = f # first, last

            while f <= n:
                steps += min(l, n) - f + 1 # inclusive + 1
                f *= 10
                l *= 10; l += 9
                # if a was 10 (so steps between 10 and 11) and n was ..., + 1 [10, 10], then [100, 109], then [1000, 1099].

            return steps

        k -= 1
        c = 1

        while k > 0:
            steps = count_between(n, c)

            if k < steps: # rooted inside --> ex: the answer is 101, and I am at 10. It is inside this tree.
                k -= 1
                c *= 10

            else: # not inside --> ex: the answer is 201, and I am at 1, so it must be inside the '2' tree
                  # ex2: the answer is 123. I am at 120. If n is a very big number, then between 120 and 121 there is an entire tree ... until I get to 123.
                k -= steps
                c += 1

        return c

    main = findKthNumber

class Solution_1298(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 1298, 'Hard')

    main = None

    def maxCandies(self, status, candies, keys, containedBoxes, initialBoxes):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximum-candies-you-can-get-from-boxes/?envType=daily-question&envId=2025-06-03

        :type status: List[int]
        :type candies: List[int]
        :type keys: List[List[int]]
        :type containedBoxes: List[List[int]]
        :type initialBoxes: List[int]
        :rtype: int
        '''

        queue = initialBoxes
        available = []
        candy = 0
        while queue:
            b = queue.pop(0)

            if status[b] == 1:
                candy += candies[b]
            else:
                available.append(b)
                continue

            available.extend(containedBoxes[b])
            for key in keys[b]:
                status[key] = 1

            for j in available[:]:
                if status[j] == 1:
                    if j not in queue:
                        queue.append(j)
                    available.remove(j)

        return candy

    main = maxCandies

class Solution_1758(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 1758, 'Hard')

    main = None

    def maxValue(self, events, k):
        '''
        Author: Kevin Zhu (ChatGPT help for DP)
        Link: https://leetcode.com/problems/maximum-number-of-events-that-can-be-attended-ii/?envType=daily-question&envId=2025-07-08

        :type events: List[List[int]]
        :type k: int
        :rtype: int
        '''

        import bisect # see problem 2040

        events.sort(key = lambda x: x[1]) # sort by end day
        n = len(events)

        end_days = [event[1] for event in events] # for binary search

        # dp[i][j]: max value using first i events, attending at most j events
        dp = [[0] * (k + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            start_day = events[i - 1][0]
            previous = bisect.bisect_right(end_days, start_day - 1) # find last event that ends before the current one starts

            for j in range(1, k + 1):
                # decide between choosing or skipping
                dp[i][j] = max(dp[i][j], dp[i - 1][j], dp[previous][j - 1] + events[i - 1][2])

        return dp[n][k] # resulting DP based its definition

    main = maxValue

class Solution_1857(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 1857, 'Hard')

    main = None

    def largestPathValue(self, colors, edges):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/largest-color-value-in-a-directed-graph/?envType=daily-question&envId=2025-05-26

        :type colors: str
        :type edges: List[List[int]]
        :rtype: int
        '''

        n = len(colors)

        # Build graph as adjacency list and indegree array
        graph = [[] for _ in range(n)]
        indegree = [0] * n
        for u, v in edges:
            graph[u].append(v)
            indegree[v] += 1

        # Initialize DP table: dp[node][color] = max count of color at node
        dp = [[0] * 26 for _ in range(n)]
        for i in range(n):
            dp[i][ord(colors[i]) - ord('a')] = 1

        # Initialize queue with nodes having indegree zero
        queue = []
        for i in range(n):
            if indegree[i] == 0:
                queue.append(i)

        visited = 0
        max_value = 0

        # BFS traversal (topological sort)
        while queue:
            node = queue.pop(0)  # pop front (acts as deque.popleft())
            visited += 1
            for neighbor in graph[node]:
                for c in range(26):
                    add = 1 if c == ord(colors[neighbor]) - ord('a') else 0
                    if dp[neighbor][c] < dp[node][c] + add:
                        dp[neighbor][c] = dp[node][c] + add
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)
            max_value = max(max_value, max(dp[node]))

        return max_value if visited == n else -1

    main = largestPathValue

class Solution_1900(Solution):
    def __init__(self):
        super().__init__('kcsquared', 1900, 'Hard')

    main = None

    def earliestAndLatest(self, n, a, b):
        '''
        Author: @kcsquared (I couldn't find any other clean & concise solutions), trickey problem.
        Link: https://leetcode.com/problems/the-earliest-and-latest-rounds-where-players-compete/?envType=daily-question&envId=2025-07-12
        Original Solution Link: https://leetcode.com/problems/the-earliest-and-latest-rounds-where-players-compete/solutions/1272828/10-lines-0ms-bit-counting-solution-o-1-time-o-1-space

        :type n: int
        :type firstPlayer: int
        :type secondPlayer: int
        :rtype: List[int]
        '''

        def ceiling_of_log2(x):
            offset = 1 if (x & (x - 1)) != 0 else 0
            x |= (x >> 1)
            x |= (x >> 2)
            x |= (x >> 4)
            x |= (x >> 8)
            x |= (x >> 16)
            return popcount(x) - 1 + offset

        def popcount(x):
            x = x - ((x >> 1) & 0x55555555)
            x = (x & 0x33333333) + ((x >> 2) & 0x33333333)
            return (((x + (x >> 4) & 0xF0F0F0F) * 0x1010101) & 0xffffffff) >> 24

        def count_trailing_zeroes(x):
            if x & 0x1:
                return 0

            c = 1

            if (x & 0xffff) == 0:
                x >>= 16
                c += 16

            if (x & 0xff) == 0:
                x >>= 8
                c += 8

            if (x & 0xf) == 0:
                x >>= 4
                c += 4

            if (x & 0x3) == 0:
                x >>= 2
                c += 2

            return c - (x & 0x1)

        if a + b == n + 1:
            return [1, 1]

        if a + b >= n + 1:
            a, b = n + 1 - b, n + 1 - a

        first_plus_second = a + b

        if a + 1 != b and first_plus_second >= (n + 1) // 2 + 1:
            if first_plus_second == n:
                if n % 4 == 2 and a + 2 == b:
                    ans_earliest = 3 + count_trailing_zeroes(n // 4)

                else:
                    ans_earliest = 3 - (a % 2)
            else:
                ans_earliest = 2

        else:
            ans_earliest = 1 + ceiling_of_log2((n + first_plus_second - 2) // (first_plus_second - 1))

            if a + 1 == b:
                ans_earliest += count_trailing_zeroes(((n + (1 << (ans_earliest - 1)) - 1) >> (ans_earliest - 1)) - 1)

        ans_latest = min(ceiling_of_log2(n), n + 1 - b)

        return [ans_earliest, ans_latest]

    main = earliestAndLatest

class Solution_1948(Solution):
    def __init__(self):
        super().__init__('ChatGPT', 1948, 'Hard')

    main = None

    def deleteDuplicateFolder(self, paths):
        '''
        Author: ChatGPT
        Link: https://leetcode.com/problems/delete-duplicate-folders-in-system/?envType=daily-question&envId=2025-07-20

        :type paths: List[List[str]]
        :rtype: List[List[str]]
        '''

        from collections import defaultdict

        class Node:
            def __init__(self):
                self.children = {}
                self.deletion_flag = False
                self.serial = ''

        root = Node()

        # Step 1: Build the folder tree (trie)
        for path in sorted(paths):
            cur = root
            for folder in path:
                if folder not in cur.children:
                    cur.children[folder] = Node()
                cur = cur.children[folder]

        # Step 2: Serialize each subtree to find duplicates
        counter = defaultdict(int)

        def dfs_serialize(node):
            if not node.children:
                return ''
            parts = []
            for name in sorted(node.children):
                child_serial = dfs_serialize(node.children[name])
                parts.append(name + '(' + child_serial + ')')
            node.serial = ''.join(parts)
            counter[node.serial] += 1
            return node.serial

        dfs_serialize(root)

        # Step 3: Mark duplicates for deletion
        def dfs_mark(node):
            if node.serial and counter[node.serial] > 1:
                node.deletion_flag = True
            for child in node.children.values():
                dfs_mark(child)

        dfs_mark(root)

        # Step 4: Collect paths excluding deleted nodes
        result = []

        def dfs_collect(node, path):
            for name, child in node.children.items():
                if child.deletion_flag:
                    continue

                result.append(path + [name])
                dfs_collect(child, path + [name])

        dfs_collect(root, [])

        return result

    main = deleteDuplicateFolder

class Solution_2014(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2014, 'Hard')

    main = None

    def longestSubsequenceRepeatedK(self, s, k):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/longest-subsequence-repeated-k-times/?envType=daily-question&envId=2025-06-27

        :type s: str
        :type k: int
        :rtype: str
        '''

        n = len(s)

        # precompute next position of the character
        next_position = [[-1] * 26 for _ in range(n + 1)]
        for i in reversed(range(n)):
            for c in range(26):
                next_position[i][c] = next_position[i + 1][c]

            next_position[i][ord(s[i]) - ord('a')] = i

        def is_valid(pattern, start_index, repetitions_needed):
            if not pattern:
                return True

            l = len(pattern)
            _i = start_index
            found = 0

            while found < repetitions_needed:
                pattern_index = 0
                temp_index = _i

                while pattern_index < l:
                    char_index = ord(pattern[pattern_index]) - ord('a')
                    next_idx = next_position[temp_index][char_index] # continue down the array for the next index of the pattern

                    if next_idx == -1:
                        return False

                    temp_index = next_idx + 1
                    pattern_index += 1

                found += 1
                _i = temp_index

            return True

        result = ''
        queue = ['']
        MAX_LENGTH = len(s) // k # abcabcab --> 3 cannot work since only 8 chars so use floor

        freq = [0] * 26
        for ch in s:
            freq[ord(ch) - ord('a')] += 1

        usable_chars = [chr(i + ord('a')) for i in range(26) if freq[i] >= k]

        while queue:
            current = queue.pop(0)

            if len(current) > len(result) or (len(current) == len(result) and current > result):
                result = current

            if len(current) >= MAX_LENGTH:
                continue

            for c in reversed(usable_chars):
                candidate = current + c

                if is_valid(candidate, 0, k):
                    queue.append(candidate)

        return result

    main = longestSubsequenceRepeatedK

class Solution_2040(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2040, 'Hard')

    main = None

    def kthSmallestProduct(self, nums1, nums2, k):
        import bisect # see problem 1758

        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/kth-smallest-product-of-two-sorted-arrays/?envType=daily-question&envId=2025-06-25

        :type nums1: List[int]
        :type nums2: List[int]
        :type k: int
        :rtype: int
        '''

        def leq(x):
            count = 0
            for i in nums1: # apply to each one: nums1[i] * nums2[...]
                if i > 0:
                    count += bisect.bisect_right(nums2, x // i)

                elif i < 0:
                    count += len(nums2) - bisect.bisect_left(nums2, -(-x // i))

                else:  # a == 0 --> 0 * array = [0] * len(array)
                    if x >= 0:
                        count += len(nums2)

            return count

        if len(nums1) > len(nums2): # nums1 is on the outside
            nums1, nums2 = nums2, nums1

        left, right = -10 ** 10, 10 ** 10 # max value

        while left < right: # binary search until left == right --> no more range of answers
            mid = (left + right) // 2

            if leq(mid) >= k:
                right = mid

            else:
                left = mid + 1

        return left

    main = kthSmallestProduct

class Solution_2081(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2081, 'Hard')

    main = None

    def kMirror(self, k, n):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/sum-of-k-mirror-numbers/?envType=daily-question&envId=2025-06-23

        :type k: int
        :type n: int
        :rtype: int
        '''

        def mirror(n, base, odd):
            result = n
            if odd:
                n //= base # remove last digit

            while n:
                result = result * base + n % base
                n //= base

            return result

        def generate(base): # generate palindrome, not a set amount --> yield
            prefix_num, total = [1] * 2, [base] * 2
            odd = 1

            while True:
                x = mirror(prefix_num[odd], base, odd)
                prefix_num[odd] += 1

                if prefix_num[odd] == total[odd]:
                    total[odd] *= base
                    odd = (odd + 1) % 2 # switch odd

                yield x

        def find_k_mirror_number(gen_base_k_palindromes):
            while True:
                candidate_num = next(gen_base_k_palindromes) # this number is already a palindrome in base k, and it is a base 10 integer

                s_candidate = str(candidate_num)

                if s_candidate == s_candidate[::-1]:
                    return candidate_num

        base1 = k

        gen_k_palindromes = generate(base1)
        return sum(find_k_mirror_number(gen_k_palindromes) for _ in range(n))

    main = kMirror

class Solution_2163(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu / ChatGPT', 2163, 'Hard')

    main = None

    def minimumDifference(self, nums):
        '''
        Author: Kevin Zhu (ChatGPT for double heap idea)
        Link: https://leetcode.com/problems/minimum-difference-in-sums-after-removal-of-elements/?envType=daily-question&envId=2025-07-18

        :type nums: List[int]
        :rtype: int
        '''

        import heapq

        n = len(nums) // 3 # should just be / 3

        # prefix sum of smallest n elements in first 2n
        max_heap = []
        for i in range(n):
            heapq.heappush(max_heap, -nums[i])  # use negative values for smallest

        prefix = [0] * (n + 1)
        prefix[0] = -sum(max_heap) # since negative

        for i in range(n):
            new_val = nums[i + n]
            # double negative: since it is already negative, add it to the value to remove
            prefix[i + 1] = prefix[i] + heapq.heappushpop(max_heap, -new_val) + new_val

        # suffix sum of largest n elements in last 2n
        min_heap = []
        for i in reversed(range(2 * n, 3 * n)):
            heapq.heappush(min_heap, nums[i])

        suffix = sum(min_heap)

        # minimum difference between the nth prefix and (nth) suffix
        result = prefix[n] - suffix

        for i in reversed(range(n)):
            new_val = nums[i + n]
            suffix += new_val - heapq.heappushpop(min_heap, new_val)
            result = min(result, prefix[i] - suffix)

        return result

    main = minimumDifference

class Solution_2163(Solution):
    def __init__(self):
        super().__init__('ChatGPT', 2322, 'Hard')

    main = None

    def minimumScore(self, nums, edges):
        '''
        Author: ChatGPT
        Link: https://leetcode.com/problems/minimum-score-after-removals-on-a-tree/?envType=daily-question&envId=2025-07-24

        :type nums: List[int]
        :type edges: List[List[int]]
        :rtype: int
        '''

        from collections import defaultdict

        '''
        My understanding of XOR:
        A XOR B, eg. 3 XOR 6, into binary -->
        0011
        0110
        ----
        0101
        A 1 bit flips the other...
        but this is implemented in Python by the ^ operator.
        '''

        n = len(nums)
        if n <= 2:
            return 0

        graph = defaultdict(list)
        for u, v in edges:
            graph[u].append(v)
            graph[v].append(u)

        # Step 1: DFS to get subtree XOR and in/out times
        in_time = [0] * n
        out_time = [0] * n
        xor = [0] * n
        time = [0]

        def dfs(u, parent):
            in_time[u] = time[0]
            time[0] += 1
            xor[u] = nums[u]

            for v in graph[u]:
                if v != parent:
                    dfs(v, u)
                    xor[u] ^= xor[v]

            out_time[u] = time[0]
            time[0] += 1

        dfs(0, -1)

        total_xor = xor[0]
        result = float('inf')

        def is_ancestor(u, v):
            return in_time[u] < in_time[v] and out_time[v] < out_time[u]

        # Step 2: Iterate through all pairs of nodes (potential second cuts)
        for i in range(1, n):
            for j in range(i + 1, n):
                a, b, c = 0, 0, 0

                # Case 1: i is an ancestor of j
                if is_ancestor(i, j):
                    a = xor[j]
                    b = xor[i] ^ xor[j]
                    c = total_xor ^ xor[i]

                # Case 2: j is an ancestor of i
                elif is_ancestor(j, i):
                    a = xor[i]
                    b = xor[j] ^ xor[i]
                    c = total_xor ^ xor[j]

                # Case 3: Neither is an ancestor of the other
                else:
                    a = xor[i]
                    b = xor[j]
                    c = total_xor ^ xor[i] ^ xor[j]

                result = min(result, max(a, b, c) - min(a, b, c))

        return result

    main = minimumScore

class Solution_2402(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2402, 'Hard')

    main = None

    def mostBooked(self, n, meetings):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/meeting-rooms-iii/?envType=daily-question&envId=2025-07-11

        :type n: int
        :type meetings: List[List[int]]
        :rtype: int
        '''

        import heapq

        meetings.sort()

        used_rooms = [] # end time, room #
        empty_rooms = list(range(n)) # empty room numbers
        heapq.heapify(empty_rooms)

        count = [0] * n # necessary tracker

        for start_time, end_time in meetings:
            while used_rooms and used_rooms[0][0] <= start_time:
                heapq.heappush(empty_rooms, heapq.heappop(used_rooms)[1]) # free any meetings that have ended and add to empty_rooms

            if empty_rooms: # Case 1: room is free
                room_number = heapq.heappop(empty_rooms)

            else: # Case 2: wait until room is free
                earliest, room_number = heapq.heappop(used_rooms) # get earliest end room
                end_time = earliest + (end_time - start_time) # shift the end time of this meeting, keeping the same duration

            count[room_number] += 1
            heapq.heappush(used_rooms, (end_time, room_number)) # mark this room as used

        return count.index(max(count))

    main = mostBooked

class Solution_3307(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3307, 'Hard')

    main = None

    def kthCharacter(self, k, operations):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/find-the-k-th-character-in-string-game-i/?envType=daily-question&envId=2025-07-03

        :type k: int
        :rtype: str
        '''

        '''
        See 'easy' problem 3304, this one just adds an extra condition for when operation[i] == 1.
        '''

        x = bin(k - 1) # how many shifts have happened, represent in binary

        count = 0

        for i, c in enumerate(reversed(x[2:])):
            if c == '1' and operations[i] == 1: # only if the operation is 1
                count += 1

        return chr(count % 26 + ord('a')) # mod isn't needed since the length constraint

    main = kthCharacter

class Solution_3333(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3333, 'Hard')

    main = None

    def possibleStringCount(self, word, k):
        '''
        Author: Kevin Zhu (used AI for dp hints)
        Link: https://leetcode.com/problems/find-the-original-typed-string-ii/?envType=daily-question&envId=2025-07-02

        :type word: str
        :type k: int
        :rtype: int
        '''

        MOD = 10 ** 9 + 7

        # count lengths of runs
        lengths = []
        prev_char = None

        for char in word:
            if char == prev_char:
                lengths[-1] += 1  # current run

            else:
                lengths.append(1)  # new run
                prev_char = char

        num_runs = len(lengths)

        total_combinations = 1
        for length in lengths:
            total_combinations = (total_combinations * length) % MOD

        if num_runs >= k: # no extra repetitions needed
            return total_combinations

        necessary = k - num_runs

        dp = [0] * necessary
        dp[0] = 1

        # use dynamic programming to find invalid solutions: ones that don't meet the length requirement
        for length in lengths:
            # prefix sums
            prefix_sums = [0] * (necessary + 1)
            for j in range(necessary):
                prefix_sums[j + 1] = (prefix_sums[j] + dp[j]) % MOD

            for j in range(necessary):
                lower_bound = j - (length - 1)
                if lower_bound <= 0:
                    dp[j] = prefix_sums[j + 1]

                else:
                    dp[j] = (prefix_sums[j + 1] - prefix_sums[lower_bound]) % MOD

        invalid_combinations = sum(dp) % MOD

        return (total_combinations - invalid_combinations) % MOD

    main = possibleStringCount

class Solution_3373(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3373, 'Hard')

    main = None

    def maxTargetNodes(self, edges1, edges2):
        '''
        Explanation for the solution:

        First, a graph is built from the edges provided for both trees.
        The graph is represented as an adjacency list (similar to 28th).
        Then, we make the parities of each tree. It determines if it is on the odd or even level.
        We use the current parity and then send the opposite parity to the next level in the DFS.
        Finally, we calculate the maximum number of target nodes based on the parity of each node.
        The amount of 'even' parity nodes is the same as the amount of nodes in Tree 1 with the same parity.
        Then, it is added to the best possible solution from Tree 2, since we can determine the node connection.
        '''

        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximize-the-number-of-target-nodes-after-connecting-trees-ii/?envType=daily-question&envId=2025-05-29

        :type edges1: List[List[int]]
        :type edges2: List[List[int]]
        :rtype: List[int]
        '''

        def build_graph(edges, n):
            graph = [[] for _ in range(n)]
            for u, v in edges:
                graph[u].append(v)
                graph[v].append(u)

            return graph

        def dfs(graph, node, parent, parity, is_even):
            count = 1 if is_even else 0
            parity[node] = is_even

            for neighbor in graph[node]:
                if neighbor != parent:
                    count += dfs(graph, neighbor, node, parity, not is_even)

            return count

        n1 = len(edges1) + 1
        n2 = len(edges2) + 1

        graph1 = build_graph(edges1, n1)
        graph2 = build_graph(edges2, n2)

        parity1 = [False] * n1
        parity2 = [False] * n2

        even_count1 = dfs(graph1, 0, -1, parity1, True)
        even_count2 = dfs(graph2, 0, -1, parity2, True)

        odd_count1 = n1 - even_count1
        odd_count2 = n2 - even_count2

        result = []
        best = max(even_count2, odd_count2)

        for i in range(n1):
            if parity1[i]:
                result.append(even_count1 + best)

            else:
                result.append(odd_count1 + best)

        return result

    main = maxTargetNodes

MOD = 10 ** 9 + 7
MAX_N = 10 ** 5

fact = [1] * MAX_N
inv_fact = [1] * MAX_N
_precomputed = False

def _power(base, exp):
    res = 1
    base %= MOD
    while exp > 0:
        if exp % 2 == 1:
            res = (res * base) % MOD
        base = (base * base) % MOD
        exp //= 2
    return res

def _nCr_mod_p(n_val, r_val):
    global _precomputed
    if not _precomputed:
        for i in range(1, MAX_N):
            fact[i] = (fact[i-1] * i) % MOD

        inv_fact[MAX_N - 1] = _power(fact[MAX_N - 1], MOD - 2)

        for i in range(MAX_N - 2, -1, -1):
            inv_fact[i] = (inv_fact[i+1] * (i+1)) % MOD

        _precomputed = True

    if r_val < 0 or r_val > n_val:
        return 0

    if r_val == 0 or r_val == n_val:
        return 1

    numerator = fact[n_val]
    denominator = (inv_fact[r_val] * inv_fact[n_val - r_val]) % MOD

    return (numerator * denominator) % MOD

class Solution_3405(Solution):
    def __init__(self):
        super().__init__('Google Gemini / Kevin Zhu', 3405, 'Hard')

    main = None

    def countGoodArrays(self, n, m, k):
        '''
        Extra functions, put them outside the class definition.

        MOD = 10 ** 9 + 7
        MAX_N = 10 ** 5

        fact = [1] * MAX_N
        inv_fact = [1] * MAX_N
        _precomputed = False

        def _power(base, exp):
            res = 1
            base %= MOD
            while exp > 0:
                if exp % 2 == 1:
                    res = (res * base) % MOD
                base = (base * base) % MOD
                exp //= 2
            return res

        def _nCr_mod_p(n_val, r_val):
            global _precomputed
            if not _precomputed:
                for i in range(1, MAX_N):
                    fact[i] = (fact[i-1] * i) % MOD

                inv_fact[MAX_N - 1] = _power(fact[MAX_N - 1], MOD - 2)

                for i in range(MAX_N - 2, -1, -1):
                    inv_fact[i] = (inv_fact[i+1] * (i+1)) % MOD

                _precomputed = True

            if r_val < 0 or r_val > n_val:
                return 0
            if r_val == 0 or r_val == n_val:
                return 1

            numerator = fact[n_val]
            denominator = (inv_fact[r_val] * inv_fact[n_val - r_val]) % MOD
            return (numerator * denominator) % MOD
        '''

        '''
        Author: Kevin Zhu, used Google Gemini
        Link: https://leetcode.com/problems/count-the-number-of-arrays-with-k-matching-adjacent-elements/?envType=daily-question&envId=2025-06-17

        :type n: int
        :type m: int
        :type k: int
        :rtype: int
        '''

        if m == 1:
            return 1 if k == n - 1 else 0

        combinations = _nCr_mod_p(n - 1, k)
        first_element_choices = m
        non_matching_count = (n - 1) - k
        non_matching_choices = _power(m - 1, non_matching_count)

        ans = (combinations * first_element_choices) % MOD
        ans = (ans * non_matching_choices) % MOD

        return ans

    main = countGoodArrays

class Solution_3445(Solution):
    def __init__(self):
        super().__init__('Google Gemini', 3445, 'Hard')

    main = None

    def maxDifference(self, s, k):
        '''
        Author: Google Gemini --> this one was just too hard!!
        Link: https://leetcode.com/problems/maximum-difference-between-even-and-odd-frequency-ii/?envType=daily-question&envId=2025-06-11

        :type s: str
        :type k: int
        :rtype: int

        Gemini Explanation:
        Core Idea: Sliding Window with Prefix Sums and State-Based Dynamic Programming
        The problem involves substrings and their properties, which immediately suggests a sliding window approach.
        Since we need to calculate frequencies efficiently within these windows, prefix sums are ideal.
        The tricky part is the parity (odd/even) and minimum value (>= 1) constraints on frequencies, which require a clever way to keep track of previous window start states.
        This leads to a form of dynamic programming or state compression where we store minimum values for specific 'left-side' states.

        gl understanding this one
        '''

        n = len(s)
        digits = [str(i) for i in range(5)]

        max_overall_diff = -float('inf')

        for char_a in digits:
            for char_b in digits:
                if char_a == char_b:
                    continue

                prefix_a = [0] * (n + 1)
                prefix_b = [0] * (n + 1) # for the i + 1

                for i in range(n):
                    prefix_a[i + 1] = prefix_a[i] + (1 if s[i] == char_a else 0)
                    prefix_b[i + 1] = prefix_b[i] + (1 if s[i] == char_b else 0)

                min_state_values = [[[ (float('inf'), 0) ] * 3 for _ in range(2)] for _ in range(2)] # it's literally a 3D array in this sort of problem ........

                min_state_values[0][0][0] = (0, 0)

                current_pair_max_diff = -float('inf')

                for right in range(n):
                    # 1. Update `min_state_values` with the new 'L' candidate that becomes valid
                    # The new `L` candidate is `right - k + 1`. This `L` represents `s[L]` as the start of a window.
                    # This update must happen *before* we try to use this `L` for the current `right` pointer.
                    # It becomes valid for forming windows of length >= k.

                    l_candidate_idx = right - k + 1
                    if l_candidate_idx >= 0: # Ensure L is a valid index for prefix sums
                        current_pa_L = prefix_a[l_candidate_idx]
                        current_pb_L = prefix_b[l_candidate_idx]

                        pa_L_parity = current_pa_L % 2
                        pb_L_parity = current_pb_L % 2

                        pb_L_cat = 0
                        if current_pb_L == 1:
                            pb_L_cat = 1
                        elif current_pb_L >= 2:
                            pb_L_cat = 2

                        val_to_store = (current_pa_L - current_pb_L, current_pb_L)

                        # Update if this `val_to_store` has a smaller (P_A[L] - P_B[L])
                        # The tuple comparison `min((a,b), (c,d))` in Python compares `a` vs `c` first, then `b` vs `d`.
                        # This works correctly for minimizing the first element.
                        min_state_values[pa_L_parity][pb_L_parity][pb_L_cat] = \
                            min(min_state_values[pa_L_parity][pb_L_parity][pb_L_cat], val_to_store)

                    # 2. Process the current window ending at `right`
                    # We only consider windows of length at least `k`.
                    if right + 1 < k:
                        continue

                    current_pa_R = prefix_a[right+1]
                    current_pb_R = prefix_b[right+1]

                    # Determine the required parities for `P_A[L]` and `P_B[L]`
                    # so that freq(a) is odd and freq(b) is even in the substring.
                    req_pa_L_parity = (current_pa_R % 2) ^ 1 # If P_A[R+1] is odd, P_A[L] must be even. If even, P_A[L] must be odd.
                    req_pb_L_parity = current_pb_R % 2      # If P_B[R+1] is odd, P_B[L] must be odd. If even, P_B[L] must be even.

                    # Iterate through all 3 possible `pb_L_value_category` states (0, 1, or >=2)
                    # to find the `L` that minimizes (P_A[L] - P_B[L]) and satisfies conditions.
                    for pb_L_cat in range(3):

                        min_tuple = min_state_values[req_pa_L_parity][req_pb_L_parity][pb_L_cat]
                        min_diff_val_L = min_tuple[0]
                        corresponding_pb_L = min_tuple[1]

                        if min_diff_val_L == float('inf'):
                            continue # No valid `L` found yet for this specific state.

                        # Reconstruct freq(a) and freq(b) for the substring s[L...right]
                        # P_A[L] = (P_A[L] - P_B[L]) + P_B[L] = min_diff_val_L + corresponding_pb_L
                        freq_a_substring = current_pa_R - (min_diff_val_L + corresponding_pb_L)
                        freq_b_substring = current_pb_R - corresponding_pb_L

                        # Final check: `freq(b)` must be at least 2.
                        # Parity checks are implicitly handled by selecting `req_pa_L_parity` and `req_pb_L_parity`.
                        if freq_b_substring >= 2:
                            # This is a valid substring. Update the max difference for the current (a, b) pair.
                            current_pair_max_diff = max(current_pair_max_diff, freq_a_substring - freq_b_substring)

                # After iterating through all 'right' for the current (a, b) pair, update the overall max.
                max_overall_diff = max(max_overall_diff, current_pair_max_diff)

        # According to the problem statement, a valid substring always exists.
        # So `max_overall_diff` should not remain -inf.
        return max_overall_diff

    main = maxDifference

class Solution_3480(Solution):
    def __init__(self):
        super().__init__('Google Gemini', 3480, 'Hard')

    main = None

    def maxSubarrays(self, n, conflictingPairs):
        '''
        Author: Kevin Zhu (first part, ish) / Gemini (getting the 'removal_gain' and 0-indexing)
        Link: https://leetcode.com/problems/maximize-subarrays-after-removing-one-conflicting-pair/submissions/1711590177/?envType=daily-question&envId=2025-07-26

        :type n: int
        :type conflictingPairs: List[List[int]]
        :rtype: int
        '''

        right = [[] for _ in range(n)]

        for a, b in conflictingPairs:
            right[max(a - 1, b - 1)].append(min(a - 1, b - 1))

        left = [-1, -1]

        removal_gain = [0] * n # gained if the most impactful conflict is removed
        answer = 0 # no removals

        for r in range(n):
            for l in right[r]:
                left = max(left, [left[0], l], [l, left[0]])

            answer += r - left[0] # MOST restrictive left value for this right

            if left[0] != -1:
                removal_gain[left[0]] += left[0] - left[1] # change if we removed the most impactful

        return answer + max(removal_gain)

    main = maxSubarrays