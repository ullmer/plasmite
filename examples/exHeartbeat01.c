/* write sample heartbeat lite3 blob to a named file (likely a pipe) using netstrings */
/* Brygg Ullmer, Clemson University */
/* October 12, 2026 */

#include <stdio.h>
#include <unistd.h>
#include <stdbool.h>
#include "lite3.h"

uint8_t buf[1024];

int main(int argc, char **argv) {
  unsigned int   sleepDur = 3;

  if (argc < 2) {
    printf("filehandle command-line argument (often a pipe) required!\n");
    return -1;
  }

  char *fnOut = argv[1];
  printf("output filename: %s\n", fnOut);
  FILE *f = fopen(fnOut, 'wb');
  if (f == NULL) {
    printf("Error opening file for writing.\n");
    return -1;
  }

  size_t buflen = 0;
  size_t bufsz = sizeof(buf);

  lite3_init_obj( buf, &buflen, bufsz);
  lite3_set_str(  buf, &buflen, 0, bufsz, "descrips", "hb");

  for (int i=0;; i++) {
    lite3_set_i64(buf, &buflen, 0, bufsz, "ingests",   i);

    printf("writing blob, byte count: %i\n", (int)buflen);
    fprintf(f, "%i:", (int)buflen);
    fwrite( f, buf, (int) buflen, 1);
    fflush( f);
    sleep(sleepDur);
  }

  return 0;
}

/* end */

