module.exports = {
  devServer: {
    proxy: {
      "^/graph": {target: "http://localhost:5000/"}
    }
  }
}
