#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, copy, time

class Logger(object):
    def __init__(self, fileOut):
        self.fileOut = open(fileOut, 'w')
    
    def log(self, message, mtype = 'message'):
        tpl = '[{0}] [{1}] {2}\n'
        self.fileOut.write(tpl.format(mtype, time.ctime(), message))
        self.fileOut.flush()

class Snake(object):
    dimensions = ('x', 'y', 'z')
    directions = {-1: '-', +1: '+'}
    ways = ((0, -1), (0, +1), (1, -1), (1, +1), (2, -1), (2, +1))

    def __init__(self, line, logger = None):
        self.logger = logger
        self.solutions = []
        self.log('Snake init')
        self.parseLine(line)
        self.state = SnakeState(self)
        
    def registerSolution(self, state):
        self.solutions.append(state)
        self.log(str(state), 'ok')

    def log(self, message, mtype = 'message'):
        if self.logger:
            self.logger.log(message, mtype); 

    def parseLine(self, line):
        self.line = line
        self.log('line: {0}'.format(self.line))
        self.len = len(self.line)
        self.log('len: {0}'.format(self.len))
        #size
        size = round(self.len ** (1/3.0))
        if size ** 3 == self.len:
            self.size = size
        else:
            msg = 'Snake wrong length. Must be cube.'
            self.log(msg, 'error')
            raise SnakeError(msg)

        # массив частей. Количество кубиков выходящих из предыдущего поворота (не включая)
        # до следующего поворота (включая)
        self.parts = [len(p) + 1 for p in self.line.split('1')]
        self.parts[0] -= 1 # первый, ниоткуда не выходит. корректируем
        self.parts[-1] -= 1 # последний не содержит следующего поворота
        # для людей просто количество кубиков в каждой части, включая концы
        self.parts_human = tuple(p + 1 for p in self.parts)
        self.log('parts: {0}'.format(str(self.parts_human)))
        self.parts_num = len(self.parts)
        self.log('parts_num: {0}'.format(self.parts_num))

    def resolve(self):
        self.log('start bruteForce')
        self.state.bruteForce()
        self.log('finish bruteForce')
        return self.solutions
    
class SnakeState(object):
    dimensions = ('x', 'y', 'z')
    directions = {-1: '-', +1: '+'}
    ways = ((0, -1), (0, +1), (1, -1), (1, +1), (2, -1), (2, +1))

    def __init__(self, snake):
        self.snake = snake
        self.position = [0] * 3
        self.world = set()
        self.world.add(tuple(self.position))
        self.borders = [{'min': p, 'max': p} for p in self.position]
        self.state = []
        self.setWay((0, +1))
        self.setWay((1, +1))

    def setWay(self, way):
        part = self.curPartLen()
        for i in range(part):
            self.position[way[0]] += way[1]
            self.world.add(tuple(self.position))
        if way[1] > 0:
            self.borders[way[0]]['max'] = max(self.borders[way[0]]['max'], self.position[way[0]])
        else:
            self.borders[way[0]]['min'] = min(self.borders[way[0]]['min'], self.position[way[0]])
        self.state.append(way)

    def curLevel(self):
        return len(self.state)

    def curPartLen(self):
        return self.snake.parts[self.curLevel()]

    def tryWay(self, way):
        print '{0} + {1}'.format(self.state, way)
        partLen = self.curPartLen()
        tryPos = self.position[:]
        for i in range(partLen):
            tryPos[way[0]] += way[1]
            if tuple(tryPos) in self.world:
                print 'posFail'
                return False
        # в итоге tryPos последняя позиция, по ней обновим мин\макс и проверим выход за границы
        tryBorders = copy.deepcopy(self.borders)
        if way[1] > 0:
            tryBorders[way[0]]['max'] = max(tryBorders[way[0]]['max'], tryPos[way[0]])
        else:
            tryBorders[way[0]]['min'] = min(tryBorders[way[0]]['min'], tryPos[way[0]])
        if tryBorders[way[0]]['max'] - tryBorders[way[0]]['min'] + 1 > self.snake.size:
            print 'borderFail'
            return False
        print 'ok'
        return True

    def isFinal(self):
        return self.curLevel() == self.snake.parts_num

    def possibleWays(self):
        return [w for w in self.ways if w[0] != self.state[-1][0]]

    def bruteForce(self):
        if self.isFinal():
            self.snake.registerSolution(self)
            return True
        tryWays = self.possibleWays()
        for tryWay in tryWays:
            if self.tryWay(tryWay):
                state = self.fork()
                state.setWay(tryWay)
                state.bruteForce()
                del state
        return False

    def fork(self):
        res = type(self)(self.snake)
        for k, v in self.__dict__.items():
            if k != 'snake':
                setattr(res, k, copy.deepcopy(v))
        return res
    
    def __str__(self):
        state = []
        for w, p in zip(self.state, self.snake.parts_human):
            state.append('{0}{1}{2}'.format(self.dimensions[w[0]], p, self.directions[w[1]]))
        return ''.join(state)

        
class SnakeError(Exception):
    pass

def main():
    p = argparse.ArgumentParser(description="Resolve snake puzzle.")
    p.add_argument("--ifile", "-i", type = str, default = 'input.txt')
    p.add_argument("--ofile", "-o", type = str, default = 'output.txt')
    opts = p.parse_args()

    fileIn = open(opts.ifile, 'r')
    snakeLine = fileIn.readline().strip()
    fileIn.close()
    logger = Logger(opts.ofile)

    snake = Snake(snakeLine, logger)
    snake.resolve()

if (__name__ == "__main__"):
    main()
