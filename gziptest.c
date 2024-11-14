#pragma wave trace(enable)

//////////////////////////// #include <stdio.h> ////////////////////////////
#define EOF     (-1)

//////////////////////////// #include "tailor.h" ////////////////////////////
#  define near

//////////////////////////// #include "gzip.h" ////////////////////////////
#define OF(args)  args
typedef void *voidp;
// L28
// #include <string.h>
    typedef typeof(sizeof(0)) size_t;
    extern void *memset (void *__s, int __c, size_t __n);
#define memzero(s, n) memset((voidp)(s), 0, (n))
// L42
#define local static
typedef unsigned char  uch;
typedef unsigned short ush;
// L109
#define EXTERN(type, array) extern type array[]
#define DECLARE(type, array, size) type array[size]
// L118
EXTERN(uch, window);
// L175
#ifndef WSIZE
#  define WSIZE 0x8000
#endif
#define MIN_MATCH  3
#define MAX_MATCH  258
#define MIN_LOOKAHEAD (MAX_MATCH+MIN_MATCH+1)
#define MAX_DIST  (WSIZE-MIN_LOOKAHEAD)
// L293
extern int (*read_buf) OF((char *buf, unsigned size));
//L307
extern void error OF((char *m));

//////////////////////////// deflate.c ////////////////////////////
// L86
#ifdef SMALL_MEM
#   define HASH_BITS  13  /* Number of bits used to hash strings */
#endif
#ifdef MEDIUM_MEM
#   define HASH_BITS  14
#endif
#ifndef HASH_BITS
#   define HASH_BITS  15
   /* For portability to 16 bit machines, do not use values above 15. */
#endif

// L107
#define HASH_SIZE (unsigned)(1<<HASH_BITS)
#define HASH_MASK (HASH_SIZE-1)

// L115
#define FAST 4
#define SLOW 2

// L122
#define head (prev+WSIZE)

DECLARE(ush, prev, WSIZE);

// L159
long block_start;
local unsigned ins_h;
#define H_SHIFT  ((HASH_BITS+MIN_MATCH-1)/MIN_MATCH)

// L178
      unsigned near strstart;
local int           eofile;
local unsigned      lookahead;
unsigned near max_chain_length;
local unsigned int max_lazy_match;

// L199
local int compr_level;
unsigned near good_match;
typedef struct config {
   ush good_length; /* reduce lazy search above this match length */
   ush max_lazy;    /* do not perform lazy search above this match length */
   ush nice_length; /* quit search above this match length */
   ush max_chain;
} config;
int near nice_match;
local config configuration_table[10] = {
/*      good lazy nice chain */
/* 0 */ {0,    0,  0,    0},  /* store only */
/* 1 */ {4,    4,  8,    4},  /* maximum speed, no lazy matches */
/* 2 */ {4,    5, 16,    8},
/* 3 */ {4,    6, 32,   32},

/* 4 */ {4,    4, 16,   16},  /* lazy matches */
/* 5 */ {8,   16, 32,   32},
/* 6 */ {8,   16, 128, 128},
/* 7 */ {8,   32, 128, 256},
/* 8 */ {32, 128, 258, 1024},
/* 9 */ {32, 258, 258, 4096}}; /* maximum compression */

// L250
local void fill_window OF((void));

// L268
#define UPDATE_HASH(h,c) (h = (((h)<<H_SHIFT) ^ (c)) & HASH_MASK)

//// ACTUAL FUNCTION WE CARE ABOUT
void lm_init (pack_level, flags)
    int pack_level; /* 0: store, 1: best speed, 9: best compression */
    ush *flags;     /* general purpose bit flag */
{
    register unsigned j;

    if (pack_level < 1 || pack_level > 9) error("bad pack level");
    compr_level = pack_level;

    /* Initialize the hash table. */
#if defined(MAXSEG_64K) && HASH_BITS == 15
    for (j = 0;  j < HASH_SIZE; j++) head[j] = NIL;
#else
    memzero((char*)head, HASH_SIZE*sizeof(*head));
#endif
    /* prev will be initialized on the fly */

    /* Set the default configuration parameters:
     */
    max_lazy_match   = configuration_table[pack_level].max_lazy;
    good_match       = configuration_table[pack_level].good_length;
#ifndef FULL_SEARCH
    nice_match       = configuration_table[pack_level].nice_length;
#endif
    max_chain_length = configuration_table[pack_level].max_chain;
    if (pack_level == 1) {
       *flags |= FAST;
    } else if (pack_level == 9) {
       *flags |= SLOW;
    }
    /* ??? reduce max_chain_length for binary files */

    strstart = 0;
    block_start = 0L;
#ifdef ASMV
    match_init(); /* initialize the asm code */
#endif

    lookahead = read_buf((char*)window,
			 sizeof(int) <= 2 ? (unsigned)WSIZE : 2*WSIZE);

    if (lookahead == 0 || lookahead == (unsigned)EOF) {
       eofile = 1, lookahead = 0;
       return;
    }
    eofile = 0;
    /* Make sure that we always have enough lookahead. This is important
     * if input comes from a device such as a tty.
     */
    while (lookahead < MIN_LOOKAHEAD && !eofile) fill_window();

    ins_h = 0;
    for (j=0; j<MIN_MATCH-1; j++) UPDATE_HASH(ins_h, window[j]);
    /* If lookahead < MIN_MATCH, ins_h is garbage, but this is
     * not important since only literal bytes will be emitted.
     */
}

#pragma wave trace(disable)
