async function connectWallet(){
  if(window.ethereum){
    const accounts = await ethereum.request({method:'eth_requestAccounts'});
    alert("Connected: " + accounts[0]);
  } else {
    alert("Install MetaMask");
  }
}
