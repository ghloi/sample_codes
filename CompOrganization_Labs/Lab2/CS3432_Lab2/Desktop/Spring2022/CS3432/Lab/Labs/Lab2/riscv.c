#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h> // malloc & free
#include <stdint.h> // use guaranteed 64-bit integers
#include "tokenizer.h" // Create header file and reference that
#include "memory.h" // built-in functions to read and write to a specific file

int32_t* reg; // Array of 32 32-bit registers

void init_regs();
bool interpret(char* instr);
void write_read_demo();

/**
 * Initialize register array for usage.
 * Malloc space for each 32-bit register then initializes each register to 0.
 * Do not alter this function!
 */
void init_regs(){
	int reg_amount = 32;
	reg = malloc(reg_amount * sizeof(int32_t)); // 32 * 4 bytes
	for(int i = 0; i < 32; i++)
		reg[i] = i;
}


/*
    Adds values in register rs1 and rs2 and puts the sum inside register rd
*/
void add(int rd, int rs1, int rs2){
    reg[rd] = reg[rs1] + reg[rs2];
}

/*
    Adds value in register rs1 to imm and puts the sum inside register rd
*/
void addi(int rd, int rs1, int imm){
    reg[rd] = reg[rs1] + imm;
}

/*
    Retrieves value at memory offset imm+areg and stores inside register rd
*/
void lw(int rd, int imm, int areg){
    int32_t chosenVal = read_address(imm+areg, "mem.txt");
    reg[rd] = chosenVal;
}

/*
    Stores value at register rd inside memory offset imm+areg
*/
void sw(int rd, int imm, int areg){
    int32_t data = reg[rd];
    int32_t address = imm+areg;
    write_address(data, address, "mem.txt");
}

/*
    Puts the bitwise and result of register rs1 and rs2 inside of register rd
*/
void and(int rd, int rs1, int rs2){
    reg[rd] = reg[rs1] & reg[rs2];
}

/*
    Puts the bitwise or result of register rs1 and rs2 inside of register rd
*/
void or(int rd, int rs1, int rs2){
    reg[rd] = reg[rs1] | reg[rs2];
}

/*
    Puts the bitwise xor result of register rs1 and rs2 inside of register rd
*/
void xor(int rd, int rs1, int rs2){
    reg[rd] = reg[rs1] ^ reg[rs2];
}

/*
    Compares two strings and returns true if they're the same, false otherwise
*/
bool comp(char first[], char second[]){
    if(getStringLength(first) != getStringLength(second)){
        return false;
    }
    for(int i = 0; i < getStringLength(first); i++){
        if(first[i] != second[i]){
            return false;
        }
    }
    return true;
}

/*
    Converts a string to an integer equivalent ("524" == 524)
*/
int convert(char string[]){
    int totalVal = atoi(string);
    return totalVal;
}

/*
    Removes the first and last char of a string and converts it to an integer
*/
int removeEdgesAndConvert(char string[]){
    int length = getStringLength(string);
    char newString[length-2];
    for(int i = 0; i < length-1; i++){ //Exclude last char "length-1"
        if(i==0){continue;}
        newString[i-1] = string[i];
    }
    return convert(newString);
}

/*
    Removes the first char of a string and converts it to an integer
*/
int removeFirstAndConvert(char string[]){
    int length = getStringLength(string);
    char newString[length-1];
    for(int i = 0; i < length; i++){
        if(i==0){continue;}
        newString[i-1] = string[i];
    }
    return convert(newString);
}

/**
 * Fill out this function and use it to read interpret user input to execute RV64 instructions.
 * You may expect that a single, properly formatted RISC-V instruction string will be passed
 * as a parameter to this function.
 */
bool interpret(char* instr){
    char** tokens = tokenize(instr, ' ');
    if( comp(tokens[0],"ADD") ){
        //Convert each token to integers, then pass to add function
        int firstReg = removeFirstAndConvert(tokens[1]);
        int secondReg = removeFirstAndConvert(tokens[2]);
        int thirdReg = removeFirstAndConvert(tokens[3]);
        
        //Pass
        add(firstReg, secondReg, thirdReg);
    }else if( comp(tokens[0], "LW") ){
        //Convert register value to integer
        int dReg = removeFirstAndConvert(tokens[1]);
        
        //Split third token into two tokens
        char** newTokens = tokenize(tokens[2], '(');
        
        //Convert first part into integer
        int imm = convert(newTokens[0]);
        
        //Take out X at beginning and ) at end and conver to integer
        int aReg = removeEdgesAndConvert(newTokens[1]);
        
        //Pass
        lw(dReg, imm, aReg);
    }else if( comp(tokens[0], "ADDI") ){
        //Same as add but without third register variable
        int firstReg = removeFirstAndConvert(tokens[1]);
        int secondReg = removeFirstAndConvert(tokens[2]);
        int thirdImm = convert(tokens[3]);
        
        //Pass
        addi(firstReg, secondReg, thirdImm);
    }else if( comp(tokens[0], "SW") ){
        //Get register and convert
        int dReg = removeFirstAndConvert(tokens[1]);
        
        //Split tokens[2] into xxx Xxx)
        char** newTokens = tokenize(tokens[2], '(');
        
        //Get value of first part of split
        int imm = convert(newTokens[0]);
        
        //Remove X from beginning and ) from end and convert to integer for second part
        int aReg = removeEdgesAndConvert(newTokens[1]);
        
        //Pass
        sw(dReg, imm, aReg);
    }else if( comp(tokens[0], "AND") ){
        //Convert each token into integers then pass into AND
        int firstReg = removeFirstAndConvert(tokens[1]);
        int secondReg = removeFirstAndConvert(tokens[2]);
        int thirdReg = removeFirstAndConvert(tokens[3]);
        
        //Pass
        and(firstReg, secondReg, thirdReg);
    }else if( comp(tokens[0], "OR") ){
        //Convert each token into integers then pass into OR
        int firstReg = removeFirstAndConvert(tokens[1]);
        int secondReg = removeFirstAndConvert(tokens[2]);
        int thirdReg = removeFirstAndConvert(tokens[3]);
        
        //Pass
        or(firstReg, secondReg, thirdReg);
    }else if( comp(tokens[0], "XOR") ){
        //Convert each token into integers then pass into XOR
        int firstReg = removeFirstAndConvert(tokens[1]);
        int secondReg = removeFirstAndConvert(tokens[2]);
        int thirdReg = removeFirstAndConvert(tokens[3]);
        
        //Pass
        xor(firstReg, secondReg, thirdReg);
    }
	return true;
}


/**
 * Simple demo program to show the usage of read_address() and write_address() found in memory.c
 * Before and after running this program, look at mem.txt to see how the values change.
 * Feel free to change "data_to_write" and "address" variables to see how these affect mem.txt
 * Use 0x before an int in C to hardcode it as text, but you may enter base 10 as you see fit.
 */
void write_read_demo(){
	int32_t data_to_write = 0xFFF; // equal to 4095
	int32_t address = 0x98; // equal to 152
	char* mem_file = "mem.txt";

	// Write 4095 (or "0000000 00000FFF") in the 20th address (address 152 == 0x98)
	int32_t write = write_address(data_to_write, address, mem_file);
	if(write == (int32_t) NULL)
		printf("ERROR: Unsucessful write to address %0X\n", 0x40);
	int32_t read = read_address(address, mem_file);

	printf("Read address %lu (0x%lX): %lu (0x%lX)\n", address, address, read, read); // %lu -> format as an long-unsigned
}

/**
 * Prints all 32 registers in column-format
 */
void print_regs(){
	int col_size = 10;
	for(int i = 0; i < 8; i++){
		printf("X%02i:%.*lld", i, col_size, (long long int) reg[i]);
		printf(" X%02i:%.*lld", i+8, col_size, (long long int) reg[i+8]);
		printf(" X%02i:%.*lld", i+16, col_size, (long long int) reg[i+16]);
		printf(" X%02i:%.*lld\n", i+24, col_size, (long long int) reg[i+24]);
	}
}

/**
 * Your code goes in the main
 *
 */
int main(){
	// Do not write any code between init_regs
	init_regs(); // DO NOT REMOVE THIS LINE

	print_regs();

	// Below is a sample program to a write-read. Overwrite this with your own code.
	//write_read_demo();

	printf(" RV32 Interpreter.\nType RV32 instructions. Use upper-case letters and space as a delimiter.\nEnter 'END' or EOF Char to end program\n");

    
	char* instruction = malloc(1000 * sizeof(char));
	bool is_null = false;
	// fgets() returns null if EOF is reached.
	is_null = fgets(instruction, 1000, stdin) == NULL;
	while(!is_null){
        if(instruction[0] == '\n'){ //For empty input I guess
            break;
        }
        instruction[getStringLength(instruction)-1] = '\0'; //Replaces \n
        if(comp(instruction, "END")){
            break;
        }
		interpret(instruction);
		printf("\n");
		print_regs();
		printf("\n");
		is_null = fgets(instruction, 1000, stdin) == NULL;
	}

	printf("Good bye!\n");

	return 0;
}
