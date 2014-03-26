#!/usr/bin/php
<?php

set_time_limit(60*60*24);
global $podhod;


function init($snake_line) {
    $snake = str_split(trim($snake_line));
    // metrics
    $length = count($snake);
    $size = round(pow($length, 1/3));
    // check size
    if (pow($size, 3) != $length) {
        echo "snake is not a cube\n";
        return false;
    }
    // split to parts
    $parts = [];
    $i = -1;
    foreach($snake as $turn) {
        $i++;
        if ($turn) {
            $parts[] = $i;
            $i = 0;
        }
    }
    $parts[] = $i;
    // variations
    $variations = pow(4, count($parts) - 1);
    // hello world
    $world = [];
    $world['size'] = $size;
    $world['parts'] = $parts;
    $world['solution'] = [];
    $world['ways'] = ['x', 'y', 'z'];
    $world['vars'] = [[0, +1], [0, -1], [1, +1], [1, -1], [2, +1], [2,-1]];
    $world['position'] = [0, 0, 0];
    $world['level'] = 0;
    $world['matrix'] = [[[],[],[]],[[],[],[]],[[],[],[]]];
    $world['matrix'][0][0][0] = 1;
    $world[+1] = $world[-1] = [0, 0, 0];
    $world['variations'] = $variations;

    $world = set($world, [0, +1]);
    //$world = set($world, [1, +1]);
    
    return $world;
}

function set($world, $var) {
    echo ' try';
    global $podhod;
    $podhod++;
    $pos = $world['position'];
    $part = $world['parts'][$world['level']];

    //заполняем мир, проверяем пустоту
    for($i = 0; $i < $part; $i++) {
        $pos[$var[0]] += $var[1];
        if (isset($world['matrix'][$pos[0]][$pos[1]][$pos[2]])) {
            return false;
        } else {
            $world['matrix'][$pos[0]][$pos[1]][$pos[2]] = 1;
        }
    }

    //обновим минимаксы
    if ($var[1] == +1) {
        $world[+1][$var[0]] = max($world[+1][$var[0]], $pos[$var[0]]);    
    } else {
        $world[-1][$var[0]] = min($world[-1][$var[0]], $pos[$var[0]]);    
    }

    //мы ещё в кубе?
    $delta = $world[+1][$var[0]] - $world[-1][$var[0]] + 1;
    if ($delta > $world['size']) {
        return false;    
    }
    
    $world['position'] = $pos;
    $world['solution'][$world['level']] = $var;
    $world['level']++;

    echo "\n", solution($world) . " ...work\n";
    echo "$podhod/" . $world['variations'] . "     [" .((int)($podhod/$world['variations']*10000))/100 . " %]";
    return $world;
}

function go($world, $var) {
    $world = set($world, $var);

    if ($world) {
        if (count($world['solution']) == count($world['parts'])) {
            //UPPI!!
            file_put_contents('a.out', "\n" . solution($world) . " ...ok\n", FILE_APPEND);    
            return true;
        }
        $ways = $world['vars'];
        foreach ($ways as $k => $v) {
            if ($v[0] == $var[0]) {
                unset($ways[$k]);    
            }    
        }

        foreach ($ways as $way) {
            go($world, $way);    
        }
    } else {
        return false;    
    }    
}

function solution($world) {
    $str = '';
    foreach ($world['solution'] as $val) {
        $str .= $world['ways'][$val[0]];
        if ($val[1] == +1) {
            $str .= '+';    
        } else {
            $str .= '-';            
        }
    }    
    return $str;
}


$snake = file_get_contents('a.in');
$world = init($snake);
if (!$world) die();
echo "init: ok\n";
print_r($world);

go($world, [1, +1]);
echo "\nthat's all\n";
