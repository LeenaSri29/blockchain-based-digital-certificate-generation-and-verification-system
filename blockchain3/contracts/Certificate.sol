pragma solidity ^0.8.0;

contract CertificateRegistry {
    mapping(string => bool) public certificates;

    function storeCertificate(string memory hash) public {
        certificates[hash] = true;
    }

    function verifyCertificate(string memory hash) public view returns(bool) {
        return certificates[hash];
    }
}
