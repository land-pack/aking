def isMatch(target, pattern):
	string_stack = []
	str_lst = list(target)
	pattern_lst = list(pattern)
	[pattern_lst.append(None) for i in range(len(str_lst))]

	for i in range(len(str_lst)):
		if len(str_lst) == 0:
			string_stack.append(0)
		elif str_lst[i] == pattern_lst[i] or pattern_lst[i+1]=="*":
			string_stack.append(1)
		elif str_lst[i] == pattern_lst[i]:
			string_stack.append(1)
		elif pattern_lst[i] == '.':
			string_stack.append(1)

		elif pattern_lst[0] == "*":
			string_stack.append(1)
			pattern_lst.insert(i+1, '*')

		elif pattern_lst[i] == "*":
			string_stack.append(1)
			pattern_lst.insert(i, pattern_lst[i-1])
		else:
			string_stack.append(0)
		print string_stack
		print pattern_lst
	return all(string_stack)

if __name__ == '__main__':
	print isMatch("aa","a")
	print isMatch("aa","aa")
	print isMatch("aaa","aa")
	print isMatch("aa", "a*")
	print isMatch("aa", ".*")
	print isMatch("ab", ".*")
	print isMatch("aab", "c*a*b")
	print isMatch("abcd", "d*")