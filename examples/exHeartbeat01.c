/* write sample heartbeat lite3 to a named file (likely a pipe */

#include <stdio.h>
#include <unistd.h>
#include <stdbool.h>
#include "lite3.h"

uint8_t buf[1024];

int main() {
  unsigned int   sleepDur = 3;

  size_t buflen = 0;
  size_t bufsz = sizeof(buf);

  lite3_init_obj( buf, &buflen, bufsz);
  lite3_set_str(  buf, &buflen, 0, bufsz, "descrips", "hb");

  for (int i=0;; i++) {
    lite3_set_i64(buf, &buflen, 0, bufsz, "ingests",   i);

    printf("bufsz: %i\n", (int)bufsz);

    sleep(sleepDur);
  }

  return 0;
}

/* end */

