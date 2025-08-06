

f1 = FileObj("data.txt")
f1.create()
f1.write("Hello World")
f1.rename("data_tmp.txt")
print(f1.size())
# you can use many functions .....
f1.remove()

fg = FileGroup("test1.txt","test2.txt","test3.txt")
fg.create_all()
fg.write_all("Hello World")

data: dict = fg.read_all()
print(data["test1.txt"]) # file1 content
# you can use many functions .....
fg.remove_all()