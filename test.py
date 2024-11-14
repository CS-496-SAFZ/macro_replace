import re

# Sample trace content with "rescanning" - ensure this matches your actual input format
text = """
/Users/frankxin/boost_1_82_0/bin.v2/libs/wave/tool/build/clang-darwin-13/release/threadapi-pthread/threading-multi/wavetool-on/test2.c:42:36: DOUBLE_AND_SQUARE(num)
  /Users/frankxin/boost_1_82_0/bin.v2/libs/wave/tool/build/clang-darwin-13/release/threadapi-pthread/threading-multi/wavetool-on/test2.c:22:9: see macro definition: DOUBLE_AND_SQUARE(x)
  invoked with
  [
    x = num
  ]
  [
    SQUARE(TRIPLE(num))
    rescanning
    [
      /Users/frankxin/boost_1_82_0/bin.v2/libs/wave/tool/build/clang-darwin-13/release/threadapi-pthread/threading-multi/wavetool-on/test2.c:12:9: see macro definition: SQUARE(x)
      invoked with
      [
        x = TRIPLE(num)
      ]
      [
        /Users/frankxin/boost_1_82_0/bin.v2/libs/wave/tool/build/clang-darwin-13/release/threadapi-pthread/threading-multi/wavetool-on/test2.c:13:9: see macro definition: TRIPLE(x)
        invoked with
        [
          x = num
        ]
        [
          ((num) * 3)
          rescanning
          [
            ((num) * 3)
          ]
        ]
        ((((num) * 3)) * (((num) * 3)))
        rescanning
        [
          ((((num) * 3)) * (((num) * 3)))
        ]
      ]
      ((((num) * 3)) * (((num) * 3)))
    ]
  ]
"""

# Improved pattern to match "rescanning" with flexible whitespace
pattern = r"(^/Users/.+?:\d+:\d+:\s+\w+\(.*?\))"
#print(re.search(pattern, text, re.MULTILINE).group(1))
print(text.split("\n")[0])


