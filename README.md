<img align="center" alt="chess board" width="700px" style="padding-right:10px;" src="https://img.freepik.com/free-vector/figures-chessboard-isometric-illustration_575670-185.jpg?w=2000" />  

# chessBrain
An attempt at a chess playing bot using deep learning. This program generates chess games and trains a neural network on those generated games iteratively.
During the game generation process moves are Selected based on the evaluation of the neural network (I'm hoping to incorporate monte carlo search here but currently I simply don’t 
have the computational power). After generating a batch of games, the neural net is then trained on samples of positions from said generated games, and their outcomes.
This process is repeated iteratively to continually improve the accuracy of the evaluation generated from the net. This process resembles and is inspired by the work done on the alpha-zero project at google

### Dependencies

* pip
* python
* pymongo
* mongoDb installed on the computer
* pytorch

### Installing

* Install all requierments

### Executing program

* Execute the main file
