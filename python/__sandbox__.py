import sys
message = "Holaaaaaaaa".encode("utf-8")
message_length = len(message)
message = (message_length).to_bytes(2, sys.byteorder) + message

print(message)

header = message[:2]
print(int.from_bytes(header, sys.byteorder, signed=False))
print(len("Holaaaaaaaa"))