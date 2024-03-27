#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

/* Return true (non-zero) if c is the delimiter character
   previously chosen by the user.
   Zero terminators are not printable (therefore false) */
bool delim_character(char c, char delim)
{
    if(c==delim){
        return true;
    }
    //printf("%c is not equal to %c\n", c, delim);
    return false;
}

/* Return true (non-zero) if c is a non-delimiter
   character.
   Zero terminators are not printable (therefore false) */
bool non_delim_character(char c, char delim)
{
    if(c == delim){
        return false;
    }
    return true;
}

/*

*/
int getStringLength(char str[]){
    int indexCount = 0;
    for(int i = 0; (str[i] != '\0'); i++){
        //printf("Str[i] = %c\n", str[i]);
        indexCount++;
    }
    return indexCount;
}

/* Returns a pointer to the first character of the next
   word starting with a non-delimiter character. Return a zero pointer if
   str does not contain any words.*/
char* word_start(char* str,char delim)
{
    char* firstWord=0;
    if (getStringLength(str) <= 0) {
        firstWord = 0;
    }else{
        for(int i = 0; i < getStringLength(str); i++){
            while(delim_character(str[i],delim) && i < getStringLength(str)){
                i++; //Skip delimeter characters until you get the first one!
            }
            firstWord = &str[i];
            return firstWord;
        }
    }
    return firstWord;
}

/* Returns a pointer to the first delimiter character of the zero
   terminated string*/
char* end_word(char* str,char delim)
{
    char* firstDelim=0;
    if (getStringLength(str) <= 0) {
        firstDelim = 0;
    }else{
        for(int i = 0; i < getStringLength(str); i++){
            while(non_delim_character(str[i],delim) && i < getStringLength(str)){
                i++; //Skip regular characters until you get the first delimeter!
            }
            firstDelim = &str[i];
            return firstDelim;
        }
    }
    return firstDelim;
}

/* Counts the number of words or tokens*/
int count_tokens(char* str,char delim)
{
    int numSubStrings = 0;
    for(int i = 0; i < getStringLength(str); i++){
        while(delim_character(str[i], delim) && i < getStringLength(str)){
            i++; //Skip excess delimeters!
        }
        while(non_delim_character(str[i], delim) && i < getStringLength(str)){
            i++;
        }
        //First SUBSTRING is from startIndex to current i
        numSubStrings++;
        
        //printf("String[%d]= %c\n", i, str[i]);
    }
    return numSubStrings;
}

/* Returns a freshly allocated new zero-terminated string
   containing <len> chars from <inStr> */
char *copy_str(char *inStr, short len, char delim)
{
    return inStr;
}

/*
    Returns pointer to specific token in pos position of inputted string (pos being which token it is)
*/
char* get_token(char* str, char delim, int pos){    
    
    char* token = NULL;
    int startIndex;
    int currentPos = 0;
    
    for(int i = 0; i < getStringLength(str); i++){
        while(delim_character(str[i], delim) && i < getStringLength(str)){
            i++; //Skip excess delimeters!
        }
        
        startIndex = i;
        while(non_delim_character(str[i], delim) && i < getStringLength(str)){
            i++; //Skip words!
        }
        
        if(currentPos == pos){
            //This is the token we want!
            token = (char*)malloc((i-startIndex) * sizeof(char));
            int tokenIndex = 0;
            for(int j = startIndex; j < i; j++){
                token[tokenIndex] = str[j];
                tokenIndex++;
                //strcat(token, str[j]);
            }
            return token;
        }
        
        currentPos++;
    }
    return token;
}

/* Returns a freshly allocated zero-terminated vector of freshly allocated
   delimiter-separated tokens from zero-terminated str.
   For example, tokenize("hello world string"), with a character delimiter
   of a space " " would result in:
     tokens[0] = "hello"
     tokens[1] = "world"
     tokens[2] = "string"
     tokens[3] = 0
*/
char** tokenize(char* str, char delim){
    int numTokens = count_tokens(str, delim); //The amount of tokens we need (words)
    
    char** newstr = malloc(numTokens * sizeof(char**)); //Allocate space
    
    //Iterate numTokens times, so that our pointer points to each pointer like a 2D Array!
    for(int i = 0; i < numTokens; i++){
        //get_token will return a pointer to a token that occurred for the i'th time (0 will be first word, 1 will be second word)
        char* currentToken = get_token(str, delim, i);
        
        //printf("Tokens[%d]: %s\n", i, currentToken);
        
        //Set pointer to pointer to token in i'th place
        newstr[i] = currentToken;
    }
    return newstr;
}

/*
    Main method for core execution of my program!

int main(){
    //TEST METHODS
    printf("TEST CASE METHOD BELOW\n");
    printf("--------------------------------------------\n");
    char input[] = "Hello,World";
    char *pinput = input;
    char deli = ',';
    
    char *x = word_start(pinput, deli);
    printf("The first letter is: %c\n", *x);
    x = end_word(pinput, deli);
    printf("The delimeter is: %c\n", *x);
    printf("--------------------------------------------\n");
    printf("TEST CASE METHOD ABOVE\n");
    //TEST METHODS
    
    
    //MAIN
    char inputChar;
    char inputString[50]; //Allocate space in case it's a long sentence
    
    //Get delimiter
    printf("Please enter the delimiter char:\n->");
    scanf("%c",&inputChar);
    
    //Clear buffer
    int c;
    while ((c = getchar()) != '\n' && c != EOF) {}
    
    //Get string to tokenize
    printf("Please enter the input string:\n->");
    scanf("%[^\n]%*c", inputString); //Ensures we can input WHOLE string
    
    //Don't need to pass a pointer through tokenize, since string parameters in functions are already pointers
    int numTokens = count_tokens(inputString, inputChar);
    
    
    
    char** tokens = tokenize(inputString, inputChar);
    printf("TESTING CASE\n");
    for(int i = 0; i < numTokens; i++){
        printf("Tokens[%d]: %s\n", i, tokens[i]);
    }
        
    //Display original unmodified string input!
    printf("Original unmodified string input was: %s\n", inputString);
    
    //Done.
}*/
