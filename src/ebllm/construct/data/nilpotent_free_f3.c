/* Independently authored exact verifier, 2026-10-24.
 * Uses trace, c2 and determinant, whereas the archived tree checks X^3.
 * All arithmetic is integer arithmetic modulo 3. No input and no randomness.
 * The declarations below allow use with the bundled freestanding Windows clang.
 * On other platforms compile with -DPORTABLE and an ordinary C compiler.
 */
#ifdef PORTABLE
#include <stdio.h>
#else
extern int printf(const char *, ...);
extern int fflush(void *);
__declspec(dllimport) void __stdcall ExitProcess(unsigned int);
#endif

static const int order[6] = {3, 4, 5, 0, 1, 2};
static int coef[3][6];
static unsigned long long nodes[7], closed[7], open_leaves;
static int residue(int x) { int r = x % 3; return r < 0 ? r + 3 : r; }

static int witness(int depth) {
    int count = 1;
    for (int j = 1; j < depth; ++j) count *= 3;
    for (int code = 0; code < count; ++code) {
        int y[6] = {0,0,0,0,0,0}, t = code;
        for (int j = 0; j < depth - 1; ++j) { y[order[j]] = t % 3; t /= 3; }
        y[order[depth - 1]] = 1;
        int a=y[0], e=y[1], i=y[2], d=y[3], g=y[4], h=y[5];
        if (residue(a + e + i)) continue;
        int u[3] = {0,0,0};
        for (int r=0; r<3; ++r)
            for (int j=0; j<6; ++j) u[r] += coef[r][j]*y[j];
        int b=residue(-u[0]), c=residue(-u[1]), f=residue(-u[2]);
        int c2=a*e+a*i+e*i-b*d-c*g-f*h;
        if (residue(c2)) continue;
        int det=a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g);
        if (!residue(det)) return 1;
    }
    return 0;
}

static void visit(int depth) {
    ++nodes[depth];
    if (depth && witness(depth)) { ++closed[depth]; return; }
    if (depth == 6) { ++open_leaves; return; }
    int col=order[depth];
    for (int code=0; code<27; ++code) {
        coef[0][col]=code%3;
        coef[1][col]=(code/3)%3;
        coef[2][col]=code/9;
        visit(depth+1);
    }
    coef[0][col]=coef[1][col]=coef[2][col]=0;
}

static int audit(void) {
    const unsigned long long expected_nodes[7]={1,27,486,6966,48627,1312929,1740852};
    const unsigned long long expected_closed[7]={0,9,228,5165,0,1248453,1740852};
    int good=1;
    unsigned long long sum=0;
    visit(0);
    for (int d=0; d<7; ++d) {
        printf("depth %d: nodes %llu closed %llu\n", d, nodes[d], closed[d]);
        sum += nodes[d];
        if (nodes[d]!=expected_nodes[d] || closed[d]!=expected_closed[d]) good=0;
        if (d<6 && nodes[d+1]!=27*(nodes[d]-closed[d])) good=0;
    }
    printf("total nodes %llu; open leaves %llu\n",sum,open_leaves);
    good = good && sum==3109888 && open_leaves==0;
    printf("exact exhaustive upper-bound audit: %s\n",good ? "PASS" : "FAIL");
    return good ? 0 : 1;
}

#ifdef PORTABLE
int main(void) { return audit(); }
#else
void mainCRTStartup(void) { int result=audit(); fflush((void*)0); ExitProcess((unsigned int)result); }
#endif
