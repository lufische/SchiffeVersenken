import sys
import importlib
client = importlib.import_module(sys.argv[1].split(".")[0])

for i in range(int(sys.argv[2])):
  client.main()
