// 1. 引入头文件
#include<iostream>
#include<fstream>
#include<cstring>
#include<sstream>
#include<iomanip>
#include<openssl/evp.h>
// iostream, fstream, string, sstream, iomanip
// openssl/evp.h

// 2. 实现 sha256_hex(string) 函数
std::string sha256_hex(const std::string&str)
{//    - EVP_MD_CTX_new()
   EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    EVP_DigestInit_ex(ctx, EVP_sha256(), NULL);
    EVP_DigestUpdate(ctx, str.data(), str.size());
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int len=0;
    EVP_DigestFinal_ex(ctx, hash, &len);
    EVP_MD_CTX_free(ctx);
//    - 返回前16字节的hex字符串（32个字符)
std::ostringstream oss;
    for (int i = 0; i < 16; ++i) {
        oss << std::hex << std::setw(2) << std::setfill('0') << (int)hash[i];
    }
    return oss.str();
}


// 3. 实现 mask_csv(input_path, output_path) 函数
void mask_csv(const std::string&input_path,const std::string &output_path)
{
//    - 用 ifstream 逐行读取
std::ifstream infile(input_path);
std::ofstream outfile(output_path);
std::string line;
//    - 前18行原样输出
for(int i=0;i<18;i++)
{
std::getline(infile,line);
outfile<<line<<std::endl;
}
//    - 第19行开始：分割字段，对第9列（交易单号）做哈希
while(std::getline(infile,line))
{
std::istringstream iss(line);
std::string field;
std::string output_line;
int col=0;
while(std::getline(iss,field,','))
{
if(col==8) // 第9列
{
field=sha256_hex(field);


}
//    

if(col!=0)
output_line+=',';
output_line+=field; 
col++;  
}
outfile<<output_line<<std::endl;//写出到 output_path
}
}
// 4. main() 函数
int main(int argc,char*argv[])
{
//    - 读取命令行参数 argv[1] argv[2]
if(argc!=3)
{
std::cerr<<"Usage: "<<argv[0]<<" <input.csv> <output.csv>"<<std::endl;
return 1;
}

//    - 调用 mask_csv()
mask_csv(argv[1],argv[2]);
//    - 打印处理结果
std::cout<<"Masking completed. Output written to "<<argv[2]<<std::endl;

return 0;
}