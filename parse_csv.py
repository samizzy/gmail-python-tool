def main():
    parsed_arr = []
    with open('./Teacher_Detail.csv', mode='r', encoding='utf-8') as f:
        for line in f:
            arr = line.replace('"',"").split(',')
            parsed_arr.append([arr[1], arr[2]])
    
    with open('./output.csv', mode='w', encoding= 'utf-8') as f:
        for el in parsed_arr:
            f.write(el[0] +'\t'+el[1]+"\n")



if __name__ == "__main__":
    main()