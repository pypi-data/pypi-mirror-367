from .Solution import Solution

class Solution_386_A(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 386, 'Medium')

    main = None

    def lexicalOrder(self, n):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/lexicographical-numbers/?envType=daily-question&envId=2025-06-08

        :type n: int
        :rtype: List[int]
        '''

        result = []

        def s(x):
            if x > n:
                return

            result.append(x)

            for i in range(10):
                a = x * 10 + i # include 0 for 10 --> 100 up to 109
                if a > n: return # efficiency
                s(a)

        for i in range(1, 10):
            s(i)

        return result

    main = lexicalOrder

class Solution_386_B(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 386, 'Medium')

    main = None

    def lexicalOrder(self, n):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/lexicographical-numbers/?envType=daily-question&envId=2025-06-08

        :type n: int
        :rtype: List[int]
        '''

        result = []

        def s(x):
            result.append(x)

            if x * 10 <= n: s(x * 10)

            if x % 10 != 9 and x < n: s(x + 1)

        s(1)

        return result

    main = lexicalOrder

class Solution_898(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 898, 'Medium')

    main = None

    def subarrayBitwiseORs(self, arr):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/bitwise-ors-of-subarrays/?envType=daily-question&envId=2025-07-31

        :type arr: List[int]
        :rtype: int
        '''

        answer = set() # all
        current = set() # at current index

        for n in arr:
            current = {n | previous for previous in current} | {n} # either add num to the previous ones we kept or start num as a new subarray
            answer |= current

        return len(answer)

    main = subarrayBitwiseORs

class Solution_909(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 909, 'Medium')

    main = None

    def snakesAndLadders(self, board):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/snakes-and-ladders/description/?envType=daily-question&envId=2025-05-31

        :type board: List[List[int]]
        :rtype: int
        '''

        flat = []
        n = len(board)
        for i in range(n - 1, -1, -1): # provided in reverse
            row = board[i]
            if (n - 1 - i) % 2 == 0:
                flat.extend(row)
            else:
                flat.extend(reversed(row))

        queue = [(0, 0)]  # (position, rolls)
        visited = set([0])
        front = 0

        n = len(flat)
        while front < len(queue):
            pos, rolls = queue[front]
            front += 1

            if pos == n - 1:
                return rolls

            for k in range(1, 7):
                next_pos = pos + k
                if next_pos >= n:
                    continue

                if flat[next_pos] != -1:
                    next_pos = flat[next_pos] - 1 # 0 index

                if next_pos not in visited:
                    visited.add(next_pos)
                    queue.append((next_pos, rolls + 1))

        return -1

    main = snakesAndLadders

class Solution_1061_A(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 1061, 'Medium')

    main = None

    def smallestEquivalentString(self, s1, s2, baseStr):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/lexicographically-smallest-equivalent-string/?envType=daily-question&envId=2025-06-05

        :type s1: str
        :type s2: str
        :type baseStr: str
        :rtype: str
        '''

        groups = []

        for a, b in zip(s1, s2):
            new_group = set([a, b])
            merged_groups = []

            # intersections
            for g in groups:
                if g & new_group:
                    new_group |= g
                    merged_groups.append(g)

            for g in merged_groups:
                groups.remove(g)

            groups.append(new_group)

        small_map = {}
        result = ''
        for c in baseStr:
            if c in small_map.keys():
                result += small_map[c]

            else:
                best = c
                for g in groups:
                    if c in g:
                        best = min(min(g), best)
                        break

                result += best
                small_map[c] = best

        return result

    main = smallestEquivalentString

class Solution_1061_B(Solution):
    def __init__(self):
        super().__init__('ChatGPT', 1061, 'Medium')

    main = None

    def smallestEquivalentString(self, s1, s2, baseStr):
        '''
        Author: ChatGPT
        Link: https://leetcode.com/problems/lexicographically-smallest-equivalent-string/?envType=daily-question&envId=2025-06-05

        :type s1: str
        :type s2: str
        :type baseStr: str
        :rtype: str
        '''

        parent = {chr(i): chr(i) for i in range(ord('a'), ord('z') + 1)}

        def find(c): # finds the min since the min --> own parent
            if parent[c] != c:
                parent[c] = find(parent[c])

            return parent[c]

        def union(a, b):
            rootA, rootB = find(a), find(b) # get the min known now
            if rootA == rootB:
                return

            if rootA < rootB:
                parent[rootB] = rootA
            else:
                parent[rootA] = rootB

        for a, b in zip(s1, s2):
            union(a, b)

        return ''.join(find(c) for c in baseStr)

    main = smallestEquivalentString

class Solution_1233(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 1233, 'Medium')

    main = None

    def removeSubfolders(self, folder):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/remove-sub-folders-from-the-filesystem/?envType=daily-question&envId=2025-07-19

        :type folder: List[str]
        :rtype: List[str]
        '''

        folder.sort()
        current_root = folder[0]
        result = [current_root]

        for f in folder[1:]:
            if not f.startswith(current_root + '/'):
                current_root = f
                result.append(f)

        return result

    main = removeSubfolders

class Solution_1353(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 1353, 'Medium')

    main = None

    def maxEvents(self, events):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximum-number-of-events-that-can-be-attended/?envType=daily-question&envId=2025-07-07

        :type events: List[List[int]]
        :rtype: int
        '''

        import heapq # simpler + more efficient than manual heaping

        events.sort() # default for tuple is lambda x: x[0], x[1]

        num = 0
        end_days = []
        event_num = 0
        n = len(events)

        day = 1

        '''
        A heap (binary min-heap) is a data structure, like a tree, where each child is <= the parent.
        Mainting this heap invariant in this way is more efficient than appending and then sorting.
        Heap: O(log n), basic: O(n log n).
        '''

        while event_num < n or end_days:
            # day < the next events day --> fast-forward
            if not end_days and day < events[event_num][0]:
                day = events[event_num][0]

            # add all event that start at this day
            while event_num < n and events[event_num][0] == day:
                heapq.heappush(end_days, events[event_num][1])
                event_num += 1

            # remove events that ended yesterday
            while end_days and end_days[0] < day:
                heapq.heappop(end_days)

            # attend the event that ends the earliest
            if end_days:
                heapq.heappop(end_days) # removes last day and restores heap invariant
                num += 1

            day += 1

        return num

    main = maxEvents

class Solution_1432(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 1432, 'Medium')

    main = None

    def maxDiff(self, num):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/max-difference-you-can-get-from-changing-an-integer/?envType=daily-question&envId=2025-06-15

        :type num: int
        :rtype: int
        '''

        a = str(num)
        b = str(num)

        for c in a:
            if int(c) < 9:
                a = a.replace(c, '9')
                break

        first = b[0]
        for c in b:
            if c == first:
                if int(c) > 1:
                    b = b.replace(c, '1')
                    break
            else:
                if int(c) > 0:
                    b = b.replace(c, '0')
                    break

        return abs(int(a) - int(b))

    main = maxDiff

class Solution_1498(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 1498, 'Medium')

    main = None

    def numSubseq(self, nums, target):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/number-of-subsequences-that-satisfy-the-given-sum-condition/?envType=daily-question&envId=2025-06-29

        :type nums: List[int]
        :type target: int
        :rtype: int
        '''

        nums.sort()

        n = len(nums)
        MOD = 10 ** 9 + 7

        answer = 0
        left = 0
        right = n - 1

        # two pointer approach
        while left <= right:
            # if n[l] + n[r] <= target, any right value <= right will work.
            if nums[left] + nums[right] <= target:
                answer += pow(2, right - left, MOD) # efficient modular exponentiation
                                                    # there are 2 ^ (r - l) values
                                                    # when you add a modded value it will work if you tak ethe final mod again
                left += 1

            else:
                # right needs to be smaller
                right -= 1

        return answer % MOD

    main = numSubseq

class Solution_1695(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 1695, 'Medium')

    main = None

    def maximumUniqueSubarray(self, nums):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximum-erasure-value/?envType=daily-question&envId=2025-07-22

        :type nums: List[int]
        :rtype: int
        '''

        visited = set()
        answer = 0
        current_sum = 0
        left = 0

        for right in range(len(nums)):
            while nums[right] in visited: # shrink the array until the current isn't in the visited
                visited.remove(nums[left])
                current_sum -= nums[left] # 'shrink'
                left += 1 # continue shrinking

            visited.add(nums[right]) # expand
            current_sum += nums[right]
            answer = max(answer, current_sum)

        return answer

    main = maximumUniqueSubarray

class Solution_1717(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 1717, 'Medium')

    main = None

    def maximumGain(self, s, x, y):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximum-score-from-removing-substrings/?envType=daily-question&envId=2025-07-23

        :type s: str
        :type x: int
        :type y: int
        :rtype: int
        '''

        def remove_pair(_s, key, score):
            stack = []
            total = 0

            first, second = key

            for c in _s:
                '''
                this stack works because it will always process the moment there is a pair
                even if it is like bbbbbaaaaa, the stack will have all the b's and then
                for each a, it will eventually match up
                if it wasw like bbcaaa, they will never be able to meet (so it won't be a substring)
                same thing for ab, which must be done after ba (if it is worth less) to maximize rewards
                '''

                if stack and stack[-1] == first and c == second:
                    stack.pop()
                    total += score

                else:
                    stack.append(c)

            return ''.join(stack), total

        if x > y: # get the optimal since order matters
            s, score_x = remove_pair(s, 'ab', x)
            s, score_y = remove_pair(s, 'ba', y)

        else:
            s, score_x = remove_pair(s, 'ba', y)
            s, score_y = remove_pair(s, 'ab', x)

        return score_x + score_y

    main = maximumGain

class Solution_1865(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 1865, 'Medium')

    class FindSumPairs(object):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/finding-pairs-with-a-certain-sum/?envType=daily-question&envId=2025-07-06
        '''

        def __init__(self, nums1, nums2):
            '''
            :type nums1: List[int]
            :type nums2: List[int]
            '''

            self.nums1 = nums1
            self.nums2 = nums2

            self.c1 = {}
            for i in nums1:
                if i in self.c1:
                    self.c1[i] += 1

                else:
                    self.c1[i] = 1

            self.c2 = {}
            for i in nums2:
                if i in self.c2:
                    self.c2[i] += 1

                else:
                    self.c2[i] = 1

        def add(self, index, val):
            '''
            :type index: int
            :type val: int
            :rtype: None
            '''

            initial = self.nums2[index]
            new_val = initial + val

            self.nums2[index] = new_val

            self.c2[initial] -= 1

            if new_val in self.c2:
                self.c2[new_val] += 1

            else:
                self.c2[new_val] = 1

        def count(self, tot):
            '''
            :type tot: int
            :rtype: int
            '''

            num = 0

            for x in self.c1:
                complement = tot - x # instead of loop through everything
                if complement in self.c2:
                    num += self.c1[x] * self.c2[complement]

            return num

    main = FindSumPairs

class Solution_2044(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2044, 'Medium')

    main = None

    def countMaxOrSubsets(self, nums):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/count-number-of-maximum-bitwise-or-subsets/?envType=daily-question&envId=2025-07-28

        :type nums: List[int]
        :rtype: int
        '''

        from collections import Counter

        dp = Counter()
        dp[0] += 1 # empty subset
        maximum_or = 0

        for num in nums:
            for val, count in list(dp.items()):
                dp[val | num] += count # because we don't know what the or is
                # if we or this num, then we can use each way to get to it from the previous one
                # --> if we can get to 5 N different ways, then if num gets us to 8, then we can then also get to 8 N additional ways

            maximum_or |= num # add the or for every num

        return dp[maximum_or]

    main = countMaxOrSubsets

class Solution_2131(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2131, 'Medium')

    main = None

    def longestPalindrome(self, words):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/longest-palindrome-by-concatenating-two-letter-words/?envType=daily-question&envId=2025-05-25

        :type colors: str
        :type edges: List[List[int]]
        :rtype: int
        '''

        count = {}
        for word in words:
            if word in count:
                count[word] += 1

            else:
                count[word] = 1

        length = 0
        center = False

        for word in list(count.keys()):
            rev = word[::-1]
            if word != rev:
                if rev in count:
                    pairs = min(count[word], count[rev])
                    length += pairs * 4
                    count[word] -= pairs
                    count[rev] -= pairs

            else:
                pairs = count[word] // 2
                length += pairs * 4
                count[word] -= pairs * 2

                if count[word] > 0: # should be odd
                    center = True

        if center:
            length += 2

        return length

    main = longestPalindrome

class Solution_2294_A(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2294, 'Medium')

    main = None

    def partitionArray(self, nums, k):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/partition-array-such-that-maximum-difference-is-k/?envType=daily-question&envId=2025-06-19

        :type nums: List[int]
        :type k: int
        :rtype: int
        '''

        nums.sort()
        result = [[nums.pop(0)]]

        for i in nums:
            if i - result[-1][0] > k:
                result.append([i])

            else:
                result[-1].append(i)

        return(len(result))

    main = partitionArray

class Solution_2294_B(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2294, 'Medium')

    main = None

    def partitionArray(self, nums, k):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/partition-array-such-that-maximum-difference-is-k/?envType=daily-question&envId=2025-06-19

        :type nums: List[int]
        :type k: int
        :rtype: int
        '''

        nums.sort()
        m, count = nums[0], 1

        for n in nums:
            if n - m > k: # you will want to fit as many as possible until you can't
                m = n
                count += 1

        return count

    main = partitionArray

class Solution_2311(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2311, 'Medium')

    main = None

    def longestSubsequence(self, s, k):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/longest-binary-subsequence-less-than-or-equal-to-k/?envType=daily-question&envId=2025-06-26

        :type s: str
        :type k: int
        :rtype: int
        '''

        val = 0
        power = 1 # current value of the one that is added
        length = 0

        for i in reversed(range(len(s))):
            if s[i] == '0':
                length += 1

            elif power + val <= k:
                length += 1
                val += power

            power *= 2

            if power > k: # cannot add anymore ones
                break

        for j in reversed(range(i)):
            if s[j] == '0':
                length += 1

        return length

    main = longestSubsequence

class Solution_2359(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2359, 'Medium')

    main = None

    def closestMeetingNode(self, edges, node1, node2):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/find-closest-node-to-given-two-nodes/?envType=daily-question&envId=2025-05-30

        :type edges: List[int]
        :type node1: int
        :type node2: int
        :rtype: int
        '''

        def distances(node):
            distance = 0
            v = set()
            r = [len(edges) * 10] * len(edges)

            while True:
                if node in v: break
                v.add(node)
                r[node] = distance
                distance += 1
                node = edges[node]
                if node == -1: break

            return r

        d1 = distances(node1)
        d2 = distances(node2)

        argmin = 0
        impossible = True

        for i in range(len(edges)):
            if d1[i] < len(edges) * 10 and d2[i] < len(edges) * 10:
                impossible = False

            if max(d1[i], d2[i]) < max(d1[argmin], d2[argmin]):
                argmin = i

        if impossible: return -1
        return argmin

    main = closestMeetingNode

class Solution_2410(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2410, 'Medium')

    main = None

    def matchPlayersAndTrainers(self, players, trainers):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximum-matching-of-players-with-trainers/?envType=daily-question&envId=2025-07-13

        :type players: List[int]
        :type trainers: List[int]
        :rtype: int
        '''

        players.sort(reverse = True)
        trainers.sort(reverse = True)

        matches = 0
        t = 0
        max_t = len(trainers)

        for player in players:
            if t == max_t:
                break

            if player <= trainers[t]: # greedy
                matches += 1
                t += 1

        return matches

    main = matchPlayersAndTrainers

class Solution_2411(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2411, 'Medium')

    main = None

    def smallestSubarrays(self, nums):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/smallest-subarrays-with-maximum-bitwise-or/?envType=daily-question&envId=2025-07-29

        :type nums: List[int]
        :rtype: List[int]
        '''

        if nums == []: return nums
        elif max(nums) == 0: return [1 for i in nums] # all 0's --> bit length = 0

        n = len(nums)
        result = [0] * n

        # last index for each bit
        num_bits = max(nums).bit_length()
        last_seen = [-1] * num_bits

        for i in reversed(range(n)):
            for b in range(num_bits):
                if nums[i] & (1 << b): # mask --> if nums[i] has 1 at the bth bit
                    last_seen[b] = i

            result[i] = max(max(last_seen) - i + 1, 1) # farthest forward you have to go to get the max possible bits

        return result

    main = smallestSubarrays

class Solution_2419(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2419, 'Medium')

    main = None

    def longestSubarray(self, nums):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/longest-subarray-with-maximum-bitwise-and/?envType=daily-question&envId=2025-07-30

        :type nums: List[int]
        :rtype: int
        '''

        # since it is AND, any number < max(nums) WILL have a bit that is 0 when nums's bit is 1 --> maximum contiguous streak of max val.

        maximum_value = max(nums)
        maximum_length = current_length = 0

        for n in nums:
            if n == maximum_value:
                current_length += 1

            else:
                maximum_length = max(current_length, maximum_length) # streak ended, see what the value of the streak was
                current_length = 0

        return max(current_length, maximum_length) # if the final is > max

    main = longestSubarray

class Solution_2434(Solution):
    '''
    Plan:
        - get min pos for every i in s
        - if s is empty, put reverse(t)
        - if t is empty, add more s
        - add the end of t while the end of t <= min(s)
    '''

    def __init__(self):
        super().__init__('Kevin Zhu', 2434, 'Medium')

    main = None

    def robotWithString(self, s):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/using-a-robot-to-print-the-lexicographically-smallest-string/?envType=daily-question&envId=2025-06-06

        :type s: str
        :rtype: str
        '''

        if len(s) <= 1:
            return s

        n = len(s)
        stack = []
        c = list(s)
        result = []

        # if at this index there is something smaller afterwards
        suffixes = [''] * n
        suffixes[-1] = s[-1]
        for i in reversed(range(n - 1)):
            suffixes[i] = min(s[i], suffixes[i + 1])

        i = 0 # tracks the current position in s for the suffixes
        while i < n or stack:
            if i < n:
                stack.append(s[i])
                i += 1

            if i == n:
                result.extend(list(reversed(stack)))
                break

            else:
                while stack and (i == n or stack[-1] <= suffixes[i]):
                    result.append(stack.pop())

        return ''.join(result)

    main = robotWithString

class Solution_2616(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2616, 'Medium')

    main = None

    def minimizeMax(self, nums, p):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/minimize-the-maximum-difference-of-pairs/?envType=daily-question&envId=2025-06-13

        :type nums: List[int]
        :type p: int
        :rtype: int
        '''

        nums = sorted(nums)
        n = len(nums)

        # Edge case: if p is 0, no pairs needed, so difference is 0
        if p == 0:
            return 0

        # smallest diff is 0, largest diff is the max - min
        left = 0
        right = nums[-1] - nums[0]
        ans = right # start with largeest diff

        # Helper function to check if we can form 'p' pairs with max_diff
        def can_form_pairs(max_diff):
            count, i = 0, 0

            while i < n - 1: # the reason why we can just loop through like this is because if it doesn't work, any deviation from the sort will be less efficient
                if nums[i + 1] - nums[i] <= max_diff:
                    count += 1
                    i += 2 # skip used

                else:
                    i += 1

                if count >= p:
                    return True

            return False

        # Binary search, more efficient than just going through all possible min-max differences
        while left <= right:
            mid = left + (right - left) // 2

            if can_form_pairs(mid):
                ans = mid # lhs of mid
                right = mid - 1

            else:
                left = mid + 1 # rhs of mid

        return ans

    main = minimizeMax

class Solution_2929(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2929, 'Medium')

    main = None

    def distributeCandies(self, n, limit):
            '''
            This solution just usees the stars and bars problem.
            It also includes exclutions for the usage of limit.
            However, since we multiply by 3, cases like (3, 3, 1) where 3 is over the limit need to be added back in.
            This is because we subtract for child 1, but child 2 has the same case which we subtract 3 times again.
            Then, for cases like (3, 3, 3), we need to subtract again since we added it back in.
            '''

            '''
            Author: Kevin Zhu
            Link: https://leetcode.com/problems/distribute-candies-among-children-ii/?envType=daily-question&envId=2025-06-01

            :type n: int
            :type limit: int
            :rtype: int
            '''

            def choose(n, k):
                if k < 0 or k > n:
                    return 0
                if k == 0 or k == n:
                    return 1
                if k == 1:
                    return n
                if k == 2:
                    return n * (n - 1) // 2
                return 0

            # Total ways without restrictions
            total = choose(n + 2, 2)

            # Subtract cases where 1 child exceeds limit
            over1 = 3 * choose(n - (limit + 1) + 2, 2) if n >= limit + 1 else 0

            # Add back cases where 2 children exceed limit
            over2 = 3 * choose(n - 2 * (limit + 1) + 2, 2) if n >= 2 * (limit + 1) else 0

            # Subtract cases where all 3 children exceed limit
            over3 = choose(n - 3 * (limit + 1) + 2, 2) if n >= 3 * (limit + 1) else 0

            return total - over1 + over2 - over3

    main = distributeCandies

class Solution_2966(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2966, 'Medium')

    main = None

    def divideArray(self, nums, k):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/divide-array-into-arrays-with-max-difference/description/?envType=daily-question&envId=2025-06-18

        :type nums: List[int]
        :type k: int
        :rtype: List[List[int]]
        '''

        nums.sort()
        result = []
        for i in range(0, len(nums), 3):
            if nums[i + 2] - nums[i] > k:
                return []

            result.append([nums[i], nums[i + 1], nums[i + 2]])

        return result

    main = divideArray

class Solution_3085(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3085, 'Medium')

    main = None

    def minimumDeletions(self, word, k):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/minimum-deletions-to-make-string-k-special/?envType=daily-question&envId=2025-06-21

        :type word: str
        :type k: int
        :rtype: int
        '''

        freqs = {}
        for c in word:
            if c in freqs:
                freqs[c] += 1

            else:
                freqs[c] = 1

        freqs = freqs.values()
        min_d = sum(freqs)

        for t in set(freqs):
            d = 0
            for f in freqs:
                if f < t:
                    d += f

                elif f > t + k:
                    d += f - (t + k)

            min_d = min(min_d, d)

        return min_d

    main = minimumDeletions

class Solution_3170(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3170, 'Medium')

    main = None

    def clearStars(self, s):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/lexicographically-minimum-string-after-removing-stars/?envType=daily-question&envId=2025-06-07

        :type s: str
        :rtype: str
        '''

        char_indices = [[] for _ in range(26)]  # one list per lowercase letter
        removals = set()

        for j, c in enumerate(s):
            if c == '*':
                for i in range(26):
                    if char_indices[i]:
                        index = char_indices[i].pop()
                        removals |= {index, j} # instead of removal, which changes list indices, just mark as removed
                        break
            else:
                char_indices[ord(c) - ord('a')].append(j)

        return ''.join(s[i] for i in range(len(s)) if i not in removals)

    main = clearStars

class Solution_3201(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3201, 'Medium')

    main = None

    def maximumLength(self, nums):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/find-the-maximum-length-of-valid-subsequence-i/?envType=daily-question&envId=2025-07-16

        :type nums: List[int]
        :rtype: int
        '''

        '''
        a run of odd + odd = even,
        a run of even + even = even,
        a run of odd + even = odd.
        We can find the longest of these runs.
        '''

        odds = 0
        evens = 0
        alternates = 1 # no matter what, it started to alternate
        previous = nums[0] % 2

        if previous:
            odds += 1

        else:
            evens += 1

        for num in nums[1:]:
            num = num % 2

            if num:
                odds += 1

            else:
                evens += 1

            if num != previous:
                alternates += 1
                previous = num

        return max(odds, evens, alternates)

    main = maximumLength

class Solution_3202(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3202, 'Medium')

    main = None

    def maximumLength(self, nums, k):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/find-the-maximum-length-of-valid-subsequence-ii/?envType=daily-question&envId=2025-07-17

        :type nums: List[int]
        :type k: int
        :rtype: int
        '''

        '''
        k = 3
        0, 1, 3, 4, 6, 7 # 1

        0, 3, 6, 9 # 0

        0, 2, 3, 5, 6, 8 # 2

        1, 2, 4, 5 # 0

        k = 4
        0, 1, 4, 5

        0, 4, 8, 12
        '''

        mod_results = []

        for mod_target in range(k): # every possible modulus result
            dp = [0] * k # dp[j] = max len subsequence such that x % k == j and two consecutive elements in the subsequence % k = mod_target

            for x in nums:
                dp[x % k] = dp[(mod_target - x) % k] + 1
                # finding the 'pair' that this would go with, then updating the max length for a future pairing

                '''
                Example:
                k = 3, mod_target = 2
                0, 5, 7, 8, 2, 1
                At x == 2: the pair would be x == 0, at x == 1: the pair would be x == 7 (7 % 3 == 1, 1 + 1 == 2)
                '''

            mod_results.append(max(dp))

        return max(mod_results)

    main = maximumLength

class Solution_3439(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3439, 'Medium')

    main = None

    def maxFreeTime(self, eventTime, k, startTime, endTime):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/reschedule-meetings-for-maximum-free-time-i/?envType=daily-question&envId=2025-07-09

        :type eventTime: int
        :type k: int
        :type startTime: List[int]
        :type endTime: List[int]
        :rtype: int
        '''

        '''
        Important: Research indicates that problem 3439 is incorrect.
        The actual description should go along the lines of...
        'What is the maximum length of one continuous free time interval you can create by removing exactly k consecutive meetings?'
        '''

        n = len(startTime)

        free_time = [0] * (n + 1)
        free_time[0] = startTime[0]

        for i in range(1, n):
            free_time[i] = startTime[i] - endTime[i - 1] # ignore the meeting

        free_time[n] = eventTime - endTime[n - 1] # free time in blocks if meetings were removed

        current = sum(free_time[:k + 1]) # if you remove all meetings, including the gap after the last meeting removed
        answer = current

        for i in range(k + 1, n + 1):
            current += free_time[i] - free_time[i - (k + 1)] # always change the current, simulate keeping the first and removing the last

            if current > answer: # only update if better
                answer = current

        return answer

    main = maxFreeTime

class Solution_3440(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3440, 'Medium')

    main = None

    def maxFreeTime(self, eventTime, startTime, endTime):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/reschedule-meetings-for-maximum-free-time-ii/?envType=daily-question&envId=2025-07-10

        :type eventTime: int
        :type startTime: List[int]
        :type endTime: List[int]
        :rtype: int
        '''

        n = len(startTime)

        gaps = [startTime[0]] + [startTime[i] - endTime[i - 1] for i in range(1, n)] + [eventTime - endTime[-1]] # gaps between meetings

        max_left = [0] * (n + 1)
        max_right = [0] * (n + 1)
        max_left[0] = gaps[0]
        max_right[n] = gaps[n]

        for i in range(1, n + 1):
            max_left[i] = max(max_left[i - 1], gaps[i]) # max gap on the left side

        for i in reversed(range(n)):
            max_right[i] = max(max_right[i + 1], gaps[i]) # max gap on the right side

        answer = max_left[n]

        for i in range(n):
            duration = endTime[i] - startTime[i]
            merged_gap = gaps[i] + gaps[i + 1]

            if duration <= max(max_left[i - 1] if i > 0 else 0, max_right[i + 2] if i + 2 <= n else 0): # can put it outside the current gap
                answer = max(answer, merged_gap + duration) # moved completely outside the gap

            else:
                answer = max(answer, merged_gap) # move meeting in gap to combine the two

        return answer

    main = maxFreeTime

class Solution_3443(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3443, 'Medium')

    main = None

    def maxDistance(self, s, k):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximum-manhattan-distance-after-k-changes/?envType=daily-question&envId=2025-06-20

        :type s: str
        :type k: int
        :rtype: int
        '''

        max_d = 0

        dirs = [('N', 'E'), ('N', 'W')] # the opposites are S W and S E, so all are taken

        for d1, d2 in dirs:
            c_max, c_min = 0, 0
            rku, rkd = k, k

            for c in s:
                if c == d1 or c == d2: # this improves efficiency by checking + and - at the same time
                    c_max += 1

                    if rkd > 0:
                        c_min += 1
                        rkd -= 1

                    else:
                        c_min -= 1

                else:
                    c_min += 1

                    if rku > 0:
                        c_max += 1
                        rku -= 1

                    else:
                        c_max -= 1

                max_d = max(max_d, c_max, c_min)

        return max_d

    main = maxDistance

class Solution_3372(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3372, 'Medium')

    main = None

    def maxTargetNodes(self, edges1, edges2, k):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximize-the-number-of-target-nodes-after-connecting-trees-i/?envType=daily-question&envId=2025-05-28

        :type edges1: List[List[int]]
        :type edges2: List[List[int]]
        :type k: int
        :rtype: List[int]
        '''

        def build_adj(edges):
            nodes = {}
            for i, j in edges:
                if i in nodes.keys():
                    nodes[i].append(j)

                else:
                    nodes[i] = [j]

                if j in nodes.keys():
                    nodes[j].append(i)

                else:
                    nodes[j] = [i]

            return nodes

        nodes1 = build_adj(edges1)
        nodes2 = build_adj(edges2)

        def target(node, max_depth, graph):
            result = set()

            def dfs(current, depth):
                if depth > max_depth:
                    return

                if current in result:
                    return

                result.add(current)

                for neighbor in graph.get(current, []):
                    dfs(neighbor, depth + 1)

            dfs(node, 0)
            return result

        max_targets2 = 0
        for node in nodes2:
            reachable = target(node, k - 1, nodes2)
            max_targets2 = max(max_targets2, len(reachable))

        result = []
        for node in nodes1:
            reachable1 = target(node, k, nodes1)
            result.append(len(reachable1) + max_targets2)

        return result

    main = maxTargetNodes

class Solution_3403(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3403, 'Medium')

    main = None

    def answerString(self, word, numFriends):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/find-the-lexicographically-largest-string-from-the-box-i/?envType=daily-question&envId=2025-06-04

        :type word: str
        :type numFriends: int
        :rtype: str
        '''

        if numFriends == 1: return word

        max_length = len(word) - numFriends + 1
        char = max(word)
        best = ''

        for i, c in enumerate(word):
            if c == char:
                cand = word[i:i + min(max_length, len(word) - i)]
                if cand > best: best = cand

        return best

    main = answerString

