#include "../include/readNetworks.hpp"

// ------------------| TwoColIter |------------------ //
void TwoColIter::open(std::string filePath)
{
    file.open(filePath);
}

bool TwoColIter::getRow(twoInt &row)
{
    std::string line;
    char comma;

    if (std::getline(file, line))
    {
        std::istringstream iss(line);
        if (!(iss >> row.first >> row.second))
        {
            iss.clear();  // Clear the fail state
            iss.seekg(0); // Move the stream position back to the beginning
            iss >> row.first >> comma >> row.second;
        }
        return true;
    }
    else
    {
        file.close();
        return false;
    }
}

// ------------------| Network |------------------ //

void Network::setFilePath(std::string filePath)
{
    std::ifstream file(filePath);
    if (!file)
    {
        std::cerr << "File not found" << std::endl;
        std::exit(-1);
    }
    this->filePath = filePath;
}

std::string Network::getFilePath()
{
    return filePath;
}

void Network::setArraysDim(int N, int E)
{
    this->N = N;
    this->E = E;
    degree.resize(N + 1, 0);
    link.resize(2 * E + 1, 0);
    pini.resize(N + 1, 0);
    pfin.resize(N + 1, 0);
}

Network readNetwork(std::string filePath)
{
    Network rawNetwork = readNetworkFile(filePath);
    std::vector<int> labels;

    if (!getLabels(rawNetwork, labels))
    {
        return rawNetwork;
    }

    return readNetworkFile(filePath, labels);
}

static Network readNetworkFile(std::string filePath, const std::vector<int> &labels)
{
    Network network;
    network.setFilePath(filePath);
    twoInt row;
    TwoColIter iter;

    int Nmax = 0;
    int Emax = 0;

    /*
    First read to get the number of edges and nodes before any other filter
    */
    iter.open(filePath);
    while (iter.getRow(row))
    {
        if (!labels.empty())
        {
            row.first = labels[row.first];
            row.second = labels[row.second];
        }

        Emax++;
        if (row.first > Nmax)
        {
            Nmax = row.first;
        }
        if (row.second > Nmax)
        {
            Nmax = row.second;
        }
    }
    network.setArraysDim(Nmax, Emax);

    /*
     Second read to fill degree and pini arrays
     */
    iter.open(filePath);
    while (iter.getRow(row))
    {
        if (!labels.empty())
        {
            row.first = labels[row.first];
            row.second = labels[row.second];
        }

        network.degree[row.first]++;
        network.degree[row.second]++;
    }

    network.pini[1] = 1;
    for (int i = 2; i <= Nmax; i++)
    {
        network.pini[i] = network.pini[i - 1] + network.degree[i - 1];
        network.pfin[i] = network.pini[i] - 1;
    }

    /*
    Third read to fill link and pfin arrays
    */
    iter.open(filePath);
    while (iter.getRow(row))
    {
        if (!labels.empty())
        {
            row.first = labels[row.first];
            row.second = labels[row.second];
        }
        network.pfin[row.first]++;
        network.pfin[row.second]++;
        network.link[network.pfin[row.first]] = row.second;
        network.link[network.pfin[row.second]] = row.first;
    }

    return network;
}

bool getLabels(Network &network, std::vector<int> &labels)
{
    labels.resize(network.N + 1);
    int Nnew = 0;
    for (int i = 1; i <= network.N; i++)
    {
        if (network.degree[i] != 0)
        {
            Nnew++;
            labels[i] = Nnew;
        }
    }
    // Check if labels are diferent from current network nodes
    if (Nnew != network.N)
    {
        return true;
    }
    return false;
}

namespace py = pybind11;

PYBIND11_MODULE(readNetwork, handle)
{
    handle.doc() = "Manages network file reading process";
    py::class_<Network>(handle, "Network")
        .def_readwrite("N", &Network::N)
        .def_readwrite("E", &Network::E)
        .def_readwrite("degree", &Network::degree)
        .def_readwrite("link", &Network::link)
        .def_readwrite("pini", &Network::pini)
        .def_readwrite("pfin", &Network::pfin);

    handle.def("read_network", &readNetwork, "Read an edge like file returning a Network instance");
}