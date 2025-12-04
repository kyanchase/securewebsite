#!/bin/bash

# Learning bash scripting

echo "Hello, World!"

name="Alice"
echo "Welcome, $name!"

fruits=("Apple" "Banana" "Cherry")
echo "Fruits: ${fruits[@]}"

for i in {1..5}; do
    echo "Number: $i"
done

a=5
b=3
if [ $a -gt $b ]; then
    echo "$a is greater than 3"
else
    echo "$a is not greater than 3"
fi

counter=1
while [ $counter -le 5 ]; do
    echo "Counter: $counter"
    ((counter++))
done

echo "Defining and calling a function:"

function greet() {
counter=$1
while [ $counter -le $2 ]; do
    echo "Counter: $counter"
    if [ $counter -eq 5 ]; then 
        echo "I am halfway through the loop."
    fi
    ((counter++))
done
}

greet 1 10