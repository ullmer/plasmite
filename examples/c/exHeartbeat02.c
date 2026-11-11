/* write sample heartbeat lite3 blob to a named file (likely a pipe) using netstrings */
/* Brygg Ullmer, Clemson University */
/* Netstrings stream framing suggested by Mignon Pelletier */
/* October 12, 2026 */

#include <stdio.h>
#include <unistd.h>
#include <stdbool.h>
#include "lite3.h"

uint8_t buf[1024];
FILE *f;

void emit_record(const uint8_t *buf, size_t buflen) {
  fprintf(f, "%zu:", buflen);
  fwrite(buf, 1, buflen, f);
  fputc(',', f);
  fflush(f);
}

int main(int argc, char **argv) {
  unsigned int   sleepDur = 3;

  if (argc < 2) {
    printf("filehandle command-line argument (often a pipe) required!\n");
    return -1;
  }

  char *fnOut = argv[1];
  printf("output filename: %s\n", fnOut);
  f = fopen(fnOut, "wb");
  if (f == NULL) {
    printf("Error opening file for writing.\n");
    return -1;
  }

  size_t buflen = 0;
  size_t bufsz = sizeof(buf);
  size_t nwritten;

  lite3_init_obj( buf, &buflen, bufsz);
  lite3_set_str(  buf, &buflen, 0, bufsz, "descrips", "hb");

  for (int i=0;; i++) {
    lite3_set_i64(buf, &buflen, 0, bufsz, "ingests",   i);

    printf("writing blob, byte count: %i\n", (int)buflen);
    emit_record(buf, buflen);
    sleep(sleepDur);
  }

  return 0;
}

/* end */
