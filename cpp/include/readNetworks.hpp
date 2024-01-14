#ifndef READ_NETWORK
#define READ_NETWORK

// ---------| Includes |---------- //
#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>

// ------| Python binding |------- //
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

struct twoInt
{
    int first;
    int second;
};

class TwoColIter
{
public:
    std::ifstream file;
    void open(std::string filePath);
    bool getRow(twoInt &row);
};

class Network
{
private:
    std::string filePath;

public:
    int N;
    int E;
    std::vector<int> degree;
    std::vector<int> link;
    std::vector<int> pini;
    std::vector<int> pfin;
    void setFilePath(std::string filePath);
    std::string getFilePath();
    void setArraysDim(int N, int E);
};

Network readNetwork(std::string filePath);
static Network readNetworkFile(std::string filePath, const std::vector<int> &labels = {});
bool getLabels(Network &network, std::vector<int> &labels);

#endif