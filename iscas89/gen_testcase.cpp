
#include<fstream>
#include<iostream>
#include<string>

std::string file_name = "./sample/test_cases.txt";

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        std::cerr << "Usage: " << argv[0] << " <bit_number>" << std::endl;
        return 1;
    }

    int bit_number = std::stoi(argv[1]);

    std::ofstream output(file_name);
    if (!output)
    {
        std::cerr << "Error opening file: " << file_name << std::endl;
        return 1;
    }

    // generate a binary test case with the specified bit number
    // from 0 to 2^bit_number - 1
    std::string binary(bit_number, '0');
    uint64_t limit = 1ULL << bit_number;
    for (uint64_t i = 0; i < limit; ++i)
    {
        for (int j = bit_number - 1; j >= 0; --j)
        {
            binary[j] = ((i >> (bit_number - 1 - j)) & 1) ? '1' : '0';
        }
        output << binary << '\n';
    }
    

    output.close();
    return 0;
}
