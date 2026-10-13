/*
 * plasmite_ingest.c
 *
 * Reads a byte stream containing:
 *
 *   <length>:<lite3_blob>,
 *
 * netstrings.
 *
 * For every complete Lite3 blob:
 *
 *   pool_append(blob, len);
 *
 * is invoked.
 * Code by CoPilot and Brygg Ullmer, Clemson University
 * Begun 2026-10-12
 */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>

#include "lite3.h"

#define RXBUF_SZ 65536

typedef struct {
  uint8_t buf[RXBUF_SZ];
  size_t len;
} rx_state_t;

/*
 * Placeholder.
 *
 * Today:
 *   append to vector/list
 *
 * Tomorrow:
 *   rust pool ABI
 *   shared memory
 *   sqlite
 *   etc
 */
static void pool_append(
  const uint8_t *blob,
  size_t blob_len)
{
  printf("POOL APPEND: %zu bytes\n", blob_len);

  /*
   * Optional Lite3 sanity test.
   */

  /*
  int64_t v;

  if (lite3_get_i64(blob, blob_len, 0, "ingests", &v) == 0) {
    printf("ingests=%lld\n", (long long)v);
  }
  */
}

/*
 * Parse one complete netstring.
 *
 * Returns:
 *
 *   1 => message returned
 *   0 => need more data
 *  -1 => malformed
 *
 * payload points directly into rx->buf
 * (zero copy).
 */

static int next_netstring(
  rx_state_t *rx,
  uint8_t **payload,
  size_t *payload_len)
{
  size_t i;
  size_t len = 0;

  /*
   * find colon
   */

  for (i = 0; i < rx->len; i++) {

    if (rx->buf[i] == ':') break;
    if (rx->buf[i] < '0' || rx->buf[i] > '9') return -1;
  }

  if (i == rx->len) return 0;

  /*
   * parse decimal length
   */

  for (size_t j = 0; j < i; j++) {

    len *= 10;
    len += rx->buf[j] - '0';
  }

  size_t payload_start = i + 1;
  size_t total_needed  = payload_start + len + 1;

  if (rx->len < total_needed) return 0;
  if (rx->buf[payload_start + len] != ',') return -1;

  *payload     = rx->buf + payload_start;
  *payload_len = len;

  /*
   * consume message
   */

  memmove(
    rx->buf,
    rx->buf + total_needed,
    rx->len - total_needed);

  rx->len -= total_needed;

  return 1;
}


int main(int argc, char **argv)
{
  FILE *fp = stdin;

  rx_state_t rx;
  memset(&rx, 0, sizeof(rx));

  for (;;) {

    /*
     * Blocking read.
     *
     * On a normal pipe/socket/file,
     * fread() blocks if no data
     * is available.
     */

    size_t n =
      fread(rx.buf + rx.len, 1, sizeof(rx.buf) - rx.len, fp);

    if (n == 0) {

      if (feof(fp)) break;
      if (ferror(fp)) { perror("fread"); break; }
    }

    rx.len += n;

    /*
     * Drain all complete messages.
     */

    while (1) {

      uint8_t *blob;
      size_t blob_len;

      int ret = next_netstring(&rx, &blob, &blob_len);

      if (ret == 0) break;

      if (ret < 0) {
        fprintf(stderr, "Malformed netstring\n"); return 1;
      }

      /*
       * Optional:
       * invoke Lite3 validation
       * here.
       */

      pool_append(blob, blob_len);
    }
  }

  return 0;
}

/// end ///
