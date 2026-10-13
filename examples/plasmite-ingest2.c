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
#include <ctype.h>

#include "lite3.h"

#define RXBUF_SZ 65536

typedef struct {
  uint8_t buf[RXBUF_SZ];

  size_t begin;
  size_t end;
} rx_state_t;


static void pool_append(
  const uint8_t *blob,
  size_t blob_len)
{
  printf("POOL APPEND: %zu bytes\n", blob_len);

  /*
   * Future:
   *   plasmite pool append
   *   Rust ABI call
   *   shared memory deposit
   *   etc.
   */
}

/*
 * Parse one netstring.
 *
 * Returns:
 *
 *   1 => complete netstring found
 *   0 => need more data
 *  -1 => malformed
 *
 * No copying.
 *
 * payload points directly into rx->buf.
 */

static int next_netstring(
  rx_state_t *rx,
  uint8_t **payload,
  size_t *payload_len)
{
  size_t i;
  size_t len = 0;

  /*
   * Allow whitespace between netstrings.
   */

  while (rx->begin < rx->end &&
       isspace(rx->buf[rx->begin]))
  {
    rx->begin++;
  }

  if (rx->begin >= rx->end)
    return 0;

  /*
   * Find colon.
   */

  for (i = rx->begin; i < rx->end; i++) {

    if (rx->buf[i] == ':')
      break;

    if (!isdigit(rx->buf[i]))
      return -1;
  }

  if (i == rx->end)
    return 0;

  /*
   * Parse decimal length.
   */

  for (size_t j = rx->begin; j < i; j++) {

    len *= 10;
    len += rx->buf[j] - '0';
  }

  size_t payload_start = i + 1;

  size_t total_needed =
    payload_start +
    len +
    1;

  if (rx->end < total_needed)
    return 0;

  if (rx->buf[payload_start + len] != ',')
    return -1;

  *payload     = rx->buf + payload_start;
  *payload_len = len;

  /*
   * Consume message.
   */

  rx->begin = total_needed;

  return 1;
}


static void compact_buffer(
  rx_state_t *rx)
{
  if (rx->begin == 0)           return;
  if (rx->begin < RXBUF_SZ / 2) return;

  memmove(
    rx->buf,
    rx->buf + rx->begin,
    rx->end - rx->begin);

  rx->end -= rx->begin;
  rx->begin = 0;
}


int main(int argc, char **argv)
{
  FILE *fp = stdin;

  if (argc > 1) {

    printf("input filename: %s\n",
         argv[1]);

    fp = fopen(argv[1], "rb");

    if (!fp) {
      perror("fopen");
      return 1;
    }
  }

  rx_state_t rx;

  memset(&rx, 0, sizeof(rx));

  for (;;) {

    compact_buffer(&rx);

    if (rx.end >= RXBUF_SZ) {
      fprintf(stderr,
          "Receive buffer exhausted\n");
      break;
    }

    size_t n = fread(rx.buf + rx.end, 1, RXBUF_SZ - rx.end, fp);

    if (n == 0) {
      if (feof(fp)) break;
      if (ferror(fp)) { perror("fread"); break; }
    }

    rx.end += n;

    while (1) {

      uint8_t *blob;
      size_t blob_len;

      int ret = next_netstring( &rx, &blob, &blob_len);

      if (ret == 0) break;
      if (ret < 0) { fprintf(stderr, "Malformed netstring\n"); return 1; }

      /*
       * Optional Lite3 sanity check:
       *
       * if (!lite3_is_valid(...))
       *   ...
       */

      pool_append(
        blob,
        blob_len);
    }
  }

  if (fp != stdin)
    fclose(fp);

  return 0;
}

/// end ///
