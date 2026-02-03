#include <stdio.h>

#define INF 999
#define ROUTER 2

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
} dt2;

static int connectcosts2[4] = {3, 1, 0, 2};
static int mincost2[4]; 


/* compute and update distance vector from the current distance table */
static int recompute_mincost2(void)
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
      if (dt2.costs[dest][via] < best)
        best = dt2.costs[dest][via];
    }

    /* update distance vector for the current dest if a better cost was found */
    if (best != mincost2[dest]) {
      mincost2[dest] = best;
      dv_changed = 1;
    }
  }

  return dv_changed;
}


/* send distance vector to all neighbours */
static void send_mincost_to_neighbors2(void)
{
  for (int n = 0; n < 4; n++) {
    /* skip the router itself */
    if (n == ROUTER)
      continue;

    /* skip none neighbours */
    if (connectcosts2[n] >= INF)
      continue;

    /* build the routing packet */
    struct rtpkt pkt;
    pkt.sourceid = ROUTER;
    pkt.destid = n;
    for (int i = 0; i < 4; i++) 
      pkt.mincost[i] = mincost2[i];

    if (TRACE) {
      printf("[t=%6.2f] node2: send its DV to node%d, DV = [", clocktime, n);
      for (int i = 0; i < 4; i++) {
        printf("%d%s", pkt.mincost[i], (i == 3 ? "]\n" : ", "));
      }
    }

    /* send this routing packet */
    tolayer2(pkt);
  }
}


/* initialize distance table and distance vector, and send that distance vector to all neighbours */
void rtinit2(void) 
{
  if (TRACE)
    printf("[t=%6.2f] node2: rtinit2() called\n", clocktime);

  /* initialize all costs to INF: dt[i][j] = INF */
  for (int dest = 0; dest < 4; dest++)
    for (int via = 0; via < 4; via++)
      dt2.costs[dest][via] = INF;

  /* update distance table's diagonals: dt[n][n] = cost(2, n) */
  for (int n = 0; n < 4; n++)
    dt2.costs[n][n] = connectcosts2[n];

  /* initialize all minimum costs to INF */
  for (int i = 0; i < 4; i++) 
    mincost2[i] = INF;

  /* update initial distance vector */
  recompute_mincost2();

  if (TRACE) {
    printf("[t=%6.2f] node2: initial DT:\n", clocktime);
    printdt2(&dt2);
  }

  /* send distance vector to neighbours */
  send_mincost_to_neighbors2();
}


/* update distance table, when a routing packet was received from a neighbour, and send the distance vector to all neighbours if it was changed */
void rtupdate2(struct rtpkt* rcvdpkt)
{
  /* sender router of this routing packet */
  int src = rcvdpkt->sourceid;

  if (TRACE) {
    printf("[t=%6.2f] node2: rtupdate2() called from node%d with new DV = [", clocktime, src);
    for (int i = 0; i < 4; i++) {
      printf("%d%s", rcvdpkt->mincost[i], (i == 3 ? "]\n" : ", "));
    }
  }

  /* only direct neighbours are allowed */
  if (connectcosts2[src] >= INF) {
    if (TRACE) 
      printf("[t=%6.2f] node2: packet ignored (src not neighbor)\n", clocktime);

    return;
  }

  /* flag for changing distance table */
  int dt_changed = 0;

  /* update distance table: dt[dest][src] = cost(2, src) + src_mincost[dest] */
  for (int dest = 0; dest < 4; dest++) {
    int newcost = connectcosts2[src] + rcvdpkt->mincost[dest];

    if (newcost > INF)
      newcost = INF;

    if (dt2.costs[dest][src] != newcost) {
      dt2.costs[dest][src] = newcost;
      dt_changed = 1;
    }
  }

  /* flag for changing distance vector */
  int dv_changed = 0;

  /* update distance vector if distance table was changed */
  if (dt_changed)
    dv_changed = recompute_mincost2();

  if (TRACE) {
    printf("[t=%6.2f] node2: DT_updated=%s, DV_updated=%s, DT:\n", clocktime, (dt_changed ? "YES" : "NO"), (dv_changed ? "YES" : "NO"));
    printdt2(&dt2);
  }

  /* send distance vector to neighbours if it was changed */
  if (dv_changed)
    send_mincost_to_neighbors2();
}


/* pretty print distance table */
void printdt2(struct distance_table* dtptr)
{
  printf("                via     \n");
  printf("   D2 |    0     1    3 \n");
  printf("  ----|-----------------\n");
  printf("     0|  %3d   %3d   %3d\n", dtptr->costs[0][0], dtptr->costs[0][1],dtptr->costs[0][3]);
  printf("dest 1|  %3d   %3d   %3d\n", dtptr->costs[1][0], dtptr->costs[1][1],dtptr->costs[1][3]);
  printf("     3|  %3d   %3d   %3d\n", dtptr->costs[3][0], dtptr->costs[3][1],dtptr->costs[3][3]);
}