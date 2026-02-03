#include <stdio.h>

#define INF 999
#define ROUTER 3

extern struct rtpkt {
  int sourceid;       /* id of sending router sending this pkt */
  int destid;         /* id of router to which pkt being sent (must be an immediate neighbor) */
  int mincost[4];     /* min cost to node 0 ... 3 */
};

extern int TRACE;
extern int YES;
extern int NO;
extern float clocktime;

extern void tolayer2(struct rtpkt packet);

static struct distance_table
{
  int costs[4][4];
} dt3;

static int connectcosts3[4] = {7, INF, 2, 0};
static int mincost3[4]; 


/* compute and update distance vector from the current distance table */
static int recompute_mincost3(void)
{
  /* flag for changing distance vector */
  int dv_changed = 0;

  for (int dest = 0; dest < 4; dest++) {
    /* minimum cost to the current dest */
    int best = INF;

    /* zero cost for dest = source */
    if (dest == ROUTER)
      best = 0;

    /* find the best cost for the current dest via all connected routers from the current distance table */
    for (int via = 0; via < 4; via++) {
      if (dt3.costs[dest][via] < best)
        best = dt3.costs[dest][via];
    }

    /* update distance vector for the current dest if a better cost was found */
    if (best != mincost3[dest]) {
      mincost3[dest] = best;
      dv_changed = 1;
    }
  }

  return dv_changed;
}


/* send distance vector to all neighbours */
static void send_mincost_to_neighbors3(void)
{
  for (int n = 0; n < 4; n++) {
    /* skip the router itself */
    if (n == ROUTER)
      continue;

    /* skip none neighbours */
    if (connectcosts3[n] >= INF)
      continue;

    /* build the routing packet */
    struct rtpkt pkt;
    pkt.sourceid = ROUTER;
    pkt.destid = n;
    for (int i = 0; i < 4; i++) 
      pkt.mincost[i] = mincost3[i];

    if (TRACE) {
      printf("[t=%6.2f] node3: send its DV to node%d, DV = [", clocktime, n);
      for (int i = 0; i < 4; i++) {
        printf("%d%s", pkt.mincost[i], (i == 3 ? "]\n" : ", "));
      }
    }

    /* send this routing packet */
    tolayer2(pkt);
  }
}


/* initialize distance table and distance vector, and send that distance vector to all neighbours */
void rtinit3(void) 
{
  if (TRACE)
    printf("[t=%6.2f] node3: rtinit3() called\n", clocktime);

  /* initialize all costs to INF: dt[i][j] = INF */
  for (int dest = 0; dest < 4; dest++)
    for (int via = 0; via < 4; via++)
      dt3.costs[dest][via] = INF;

  /* update distance table's diagonals: dt[n][n] = cost(3, n) */
  for (int n = 0; n < 4; n++)
    dt3.costs[n][n] = connectcosts3[n];

  /* initialize all minimum costs to INF */
  for (int i = 0; i < 4; i++) 
    mincost3[i] = INF;

  /* update initial distance vector */
  recompute_mincost3();

  if (TRACE) {
    printf("[t=%6.2f] node3: initial DT:\n", clocktime);
    printdt3(&dt3);
  }

  /* send distance vector to neighbours */
  send_mincost_to_neighbors3();
}


/* update distance table, when a routing packet was received from a neighbour, and send the distance vector to all neighbours if it was changed */
void rtupdate3(struct rtpkt* rcvdpkt)
{
  /* sender router of this routing packet */
  int src = rcvdpkt->sourceid;

  if (TRACE) {
    printf("[t=%6.2f] node3: rtupdate3() called from node%d with new DV = [", clocktime, src);
    for (int i = 0; i < 4; i++) {
      printf("%d%s", rcvdpkt->mincost[i], (i == 3 ? "]\n" : ", "));
    }
  }

  /* only direct neighbours are allowed */
  if (connectcosts3[src] >= INF) {
    if (TRACE) 
      printf("[t=%6.2f] node3: packet ignored (src not neighbor)\n", clocktime);

    return;
  }

  /* flag for changing distance table */
  int dt_changed = 0;

  /* update distance table: dt[dest][src] = cost(3, src) + src_mincost[dest] */
  for (int dest = 0; dest < 4; dest++) {
    int newcost = connectcosts3[src] + rcvdpkt->mincost[dest];

    if (newcost > INF)
      newcost = INF;

    if (dt3.costs[dest][src] != newcost) {
      dt3.costs[dest][src] = newcost;
      dt_changed = 1;
    }
  }

  /* flag for changing distance vector */
  int dv_changed = 0;

  /* update distance vector if distance table was changed */
  if (dt_changed)
    dv_changed = recompute_mincost3();

  if (TRACE) {
    printf("[t=%6.2f] node3: DT_updated=%s, DV_updated=%s, DT:\n", clocktime, (dt_changed ? "YES" : "NO"), (dv_changed ? "YES" : "NO"));
    printdt3(&dt3);
  }

  /* send distance vector to neighbours if it was changed */
  if (dv_changed)
    send_mincost_to_neighbors3();
}


/* pretty print distance table */
void printdt3(struct distance_table* dtptr)
{
  printf("             via     \n");
  printf("   D3 |    0     2 \n");
  printf("  ----|-----------\n");
  printf("     0|  %3d   %3d\n", dtptr->costs[0][0], dtptr->costs[0][2]);
  printf("dest 1|  %3d   %3d\n", dtptr->costs[1][0], dtptr->costs[1][2]);
  printf("     2|  %3d   %3d\n", dtptr->costs[2][0], dtptr->costs[2][2]);
}