import json
import sys


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python oas_stat.py <oas_file>")
        sys.exit(1)
    target = sys.argv[1]
    f = open("spec/" + target + ".json", "r")
    oas = json.load(f)
    f.close()

    f = open("spec/" + target + "_endpoints.txt", "w", encoding="utf-8")
    for path in oas["paths"]:
        for method in oas["paths"][path]:
            f.write(method + " " + path + "\n")
            print(method, path)
    f.close()
    
