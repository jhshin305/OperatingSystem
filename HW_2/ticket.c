#include "stdio.h"
#include "stdbool.h"

int ticket = 0;
int turn = 0;
int count = 0;

void fetch_and_add(int* a, int* b) {
	int tmp = *b;
	*b = *a + tmp;
	*a = tmp;
}

void acquire() {
    int my_ticket = 1;
    fetch_and_add(&my_ticket, &ticket);
    while (turn != my_ticket) {
		;
	}
}

void critical_section() {
	count++;
}

void release() {
	int tmp = 1;
	fetch_and_add(&tmp, &turn);
}

int main() {
	int bx; //ticket.s에서 %bx를 초기화하지 않았다.
	while(bx) {
		acquire();
		critical_section();
		release();
		bx--;
	}

	return 0;
}