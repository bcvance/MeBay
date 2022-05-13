string = "10000000.00"

def test(string):
    while(True):
        for i in range(len(string)):
            if string[i] == "," or string[i] == ".":
                if i <= 3:
                    print(string, str(i))
                    return
                string = string[0:i-3] + "," + string[i-3:]
                break
test(string)