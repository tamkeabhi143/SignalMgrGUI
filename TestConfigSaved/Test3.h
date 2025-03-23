#ifndef TEST3_H
#define TEST3_H

#include <stdint.h>
#include <stdbool.h>

/* Automotive data type definitions */
typedef unsigned char uint8;
typedef unsigned short uint16;
typedef unsigned int uint32;
typedef unsigned long long uint64;
typedef signed char sint8;
typedef signed short sint16;
typedef signed int sint32;
typedef signed long long sint64;
typedef float float32;
typedef double float64;
typedef char char_t;
typedef unsigned char bool_t;

/* Structure type definitions */
typedef struct {
    bool_t flag_b;
    bool_t flag_b;
} TestDataV1_t;

typedef struct {
    bool_t flag_b;
    bool_t flag_b;
} TestDataV2_t;

/* Signal type definitions */
extern TestDataV1_t TestDataV1;
extern TestDataV2_t TestDataV2;

/* Default initialization values */

/* Signal accessor function declarations */
void Get_TestDataV1(TestDataV1_t* value);
void Set_TestDataV1(const TestDataV1_t* value);
void Get_TestDataV2(TestDataV2_t* value);
void Set_TestDataV2(const TestDataV2_t* value);

#endif /* TEST3_H */
