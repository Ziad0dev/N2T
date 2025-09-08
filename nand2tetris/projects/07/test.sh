# Create test_all.sh
cat > test_all.sh << 'EOF'
#!/bin/bash

echo "Testing Project 7..."
cd /home/dev/Documents/workspace/N2T/nand2tetris/projects/07

echo "SimpleAdd..."
python vm_trans.py StackArithmetic/SimpleAdd/SimpleAdd.vm

echo "StackTest..."  
python vm_trans.py StackArithmetic/StackTest/StackTest.vm

echo "BasicTest..."
python vm_trans.py MemoryAccess/BasicTest/BasicTest.vm

echo "PointerTest..."
python vm_trans.py MemoryAccess/PointerTest/PointerTest.vm

echo "StaticTest..."
python vm_trans.py MemoryAccess/StaticTest/StaticTest.vm

echo "Testing Project 8..."
cd ../08

echo "BasicLoop..."
python ../07/vm_trans.py ProgramFlow/BasicLoop/BasicLoop.vm

echo "FibonacciSeries..."
python ../07/vm_trans.py ProgramFlow/FibonacciSeries/FibonacciSeries.vm

echo "SimpleFunction..."
python ../07/vm_trans.py FunctionCalls/SimpleFunction/SimpleFunction.vm

echo "FibonacciElement..."
python ../07/vm_trans.py FunctionCalls/FibonacciElement/

echo "StaticsTest..."
python ../07/vm_trans.py FunctionCalls/StaticsTest/

echo "All tests completed!"
EOF

chmod +x test_all.sh
./test_all.sh
