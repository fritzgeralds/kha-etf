def udfs():
    count = 4
    udfs = []
    udf = []
    for i in range(count):
        udfs += 2 * [i + 1]

    print(udfs)

    for i in udfs[::2]:
        code = 'code_' + str(i)
        desc = 'desc_' + str(i)
        udf.append({code: i, desc: i})

    print(udf)

if __name__ == "__main__":
    udfs()
