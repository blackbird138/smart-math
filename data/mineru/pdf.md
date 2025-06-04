# A  

# 题目大意  

给出一个仅由大小写字母组成的字符串S(|S|<100)，输出期中的大写字母按原字符串顺序排成的串。  

# 题解  

按照题意模拟即可。  

# Code  

#include<bits/stdc++.h>   
using namespace std;   
char s[105];   
signed main()   
L scanf("%s",s+1); int n=strlen $( 5 + 1 )$ ： for(int $\mathbf { i = 1 }$ ;i<=n;++i) if(s[i]>='A'&&s[i]<='Z') putchar(s[i]); return 0;  

# B  

# 题目大意  

有一个空队列，有 $Q ( Q \leq 1 0 0 )$ 次操作，每次操作要么在队列末尾插入一个数 $X ( X \leq 1 0 0 )$ ；要么查询队首的数，并将队首出队。  

# 题解  

模拟一个队列即可，可以调用STL的queue，也可以手写一个队列。  

Code  

using namespace std;   
int q;   
queue<int> qu;   
signed main()   
{ scanf("%d",&q); while(q--) { int opt; scanf("%d",&opt); $\scriptstyle \mathbf { i } + ( o p t = = 1 )$ { int x; scanf("%d",&x); qu.push(x); } else { printf("%d\n",qu.front()); qu.pop(); } 了 return 0;  

# 题目大意  

有 $N ( N \leq 3 \times 1 0 ^ { 5 } )$ 种食材和 $M ( M \leq 3 \times 1 0 ^ { 5 } )$ 道菜，每道菜需要 $K _ { i } ( \sum K _ { i } \le 3 \times 1 0 ^ { 5 } )$ 食材制作而成。有一个长度为 $N$ 的排列 $B _ { 1 } , B _ { 2 } , \ldots , B _ { n }$ ，求出对 $B$ 每个前缀，仅使用这个前缀的食材能做出多少道菜。  

# 题解  

在输入的时候处理若干个集合 ${ \cal S } _ { 1 } , { \cal S } _ { 2 } , \ldots , { \cal S } _ { N }$ ，每个集合 $S _ { i }$ 内分别存储食材 $i$ 会在哪些菜中使用。并记录 $c n t _ { 1 } , c n t _ { 2 } , \dots , c n t _ { M }$ 表示菜 $i$ 还缺 $c n t _ { i }$ 种食材才能做出，最初 $c n t _ { i } = K _ { i }$ 。随后每增加一个食材 $x$ ，利用 $S _ { x }$ 求出所有需要 $x$ 食材的菜，并将它们所需的食材数 $c n t _ { i }$ 减少一，这样若一个菜 $y$ 有$c n t _ { y } = 0$ 则说明它能被做出了。统计数量即可。时间复杂度 $\begin{array} { r } { \mathrm { O } ( N + M + \sum K _ { i } ) } \end{array}$ 点  

Code  

using namespace std;   
const int $N = 3 \equiv 5 + 5$ ：   
int n,m,cnt[N];   
vector<int>S[N];   
signed main()   
{ scanf("%d%d",&n,&m); for(int i=1;i<=m;++i) [ int k,x; scanf("%d",&k); for(int j=1;j<=k;++j) { scanf("%d",&x); S[x].push_back(i); } cnt[i]=k; } int $\tt a m 5 = \tt a$ ： for(int i=1;i<=n;++i) { int b; scanf("%d",&b); for(auto j:S[b]) T cnt[j]--; if(!cnt[j]) ans++; } printf("%d\n",ans); } return 0;  

# 题目大意  

有一个圆上均匀顺时针排布着 $N ( N \leq 1 0 ^ { 6 } )$ 个点，且有 $M ( M \leq 3 \times 1 0 ^ { 5 } )$ 条线，每条线连接一对点，求有多少对线相交 (注意圆外部也可以相交)。  

# 题解  

我们不妨反着考虑，相交对数 $\mathbf { \sigma } = \mathbf { \sigma }$ 总对数-不相交对数。对于不相交对数，也即平行对数，因为平行有传递性，故可以统计出所有平行线构成的极大集合，这样每个极大集合内部选取一对线都必定是平行的，且平行的线对必定属于同一集合。  

那么如何求出这些集合，首先要能判断两线是否平行，观察即可发现平行的充要条件是两端点 $A _ { i } , B _ { i }$ 的 $( A _ { i } + B _ { i } )$ mod $\scriptstyle { n }$ 相同。故记 $c n t _ { x }$ 为 $( A _ { i } + B _ { i } )$ mod $n = x$ 的 $i$ 的数量，则 $a n s =$ $\begin{array} { r } { \frac { m ( m - 1 ) } { 2 } - \sum _ { x } \frac { c n t _ { x } ( c n t _ { x } - 1 ) } { 2 } } \end{array}$ 。时间复杂度 $\mathrm { O } ( N + M )$  

注意要开longlong。  

# Code  

#include<bits/stdc++.h>   
using namespace std;   
const int $N = 1 \div 5 + 5$   
int n,m,cnt[N];   
signed main()   
{ scanf("%d%d",&n,&m); for(int $\scriptstyle \mathbf { i } = \mathbf { 1 } , \mathbf { i } < = \scriptstyle \operatorname { m } _ { \mathbf { j } } + + \mathbf { i } )$ { int x,y; scanf("%d%d",&x,&y); cnt[(x+y)%n]++; ！ long long $a \nwarrow = m ^ { * } \pm 1 1 1 ^ { * } ( m { - } 1 ) / 2 ;$ - for(int i=0;i<n;++i) ans- $\mathbf { \sigma } = \mathbf { \sigma }$ cnt[i]\*1ll\*(cnt[i]-1)/2; printf("%lld\n",ans); return 0;  

# 题目大意  

有 $N ( N \leq 8 )$ 个问题，每个问题有一个分数 $S _ { i }$ 和提交的花费 $C _ { i }$ ，且有 $P _ { i } \%$ 的概率通过，每个题的通过概率互相独立。最初有 $X$ 元，每轮可以选择一个未通过的题目并花费对应的 $C _ { i }$ 提交，若通过则获得其分数，否则不会得到任何分数。提交过程中必须保证总花费不超过 $X$ 。求在最优提交策略下最终的期望得分最大是多少。  

# 题解  

由于 $N$ 很小，考虑状压dp，压缩每一个问题是否已解决的状态，即记 $f _ { i , 5 }$ 表示已经花费 $i$ 元且已解  
决的问题集合为 $\boldsymbol { \bar { s } }$ 的最大期望得分，那么转移即枚举下一个提交的问题，即  
（20 $\begin{array} { r } { f _ { i , S } = \operatorname* { m a x } _ { x \in S } \left( \frac { P _ { x } } { 1 0 0 } ( f _ { i - C _ { x } , S \backslash \{ x \} } + S _ { x } ) + \frac { 1 0 0 - P _ { x } } { 1 0 0 } f _ { i - C _ { x } , S } \right) } \end{array}$ （20  
最后对所有 $f _ { i , { \bar { S } } }$ 取最大值即答案。时间复杂度 $\mathrm { O } ( N X 2 ^ { N } )$ （204号  

# Code  

#include<bits/stdc++.h>   
using namespace std;   
const int $N = \pm \frac { 1 0 } { 1 0 }$ $x = 5 \theta \theta 5$ ：   
int n,x,s[N],c[N],p[N];   
double f[X][1<<N];   
signed main()   
{ scanf("%d%d",&n,&x); for(int $\scriptstyle { \mathbf { i } = 1 , \mathbf { i } < = \ n _ { s } + + \mathbf { i } } )$ scanf("%d%d%d",&s[i],&c[i],&p[i]); double $\tt a n 5 = 0$ for(int $\mathbf { i } { = } 1 , \mathbf { i } \in \mathrm { { x } , + } + 1 \mathrm { { i } } )$ for(int $\dot { \bf { \cal J } } = \hat { \Theta }$ ：j<(1<<n）;++j) { for(int k=0;k<n;++k) if(（(j>>k)&1）==1&&c[k+1]<=i） f[i][j]=max(f[i][j]，p[k+1]/100.0 \*(f[i-c[k+ + (100-p[k+1])/100.0 \* f[i-c[k+ ans $\mathbf { \sigma } _ { = }$ max(ans,f[i][j]); 于 printf("%.91f\n",ans); return 0;  

# 题目大意  

有一个 $N \times N ( N \leq 2 0 )$ 的网格图，每个网格上有一个 $0 \sim 9$ 的数字。最开始从左上角 $( 1 , 1 )$ ，每次只能向右或向下走一格，最终经过 $2 N - 2$ 步走到 $( N , N )$ ，此时将路径上所有网格的数字依次连接到一起得到一个数 $\boldsymbol { S }$ ，求 $\boldsymbol { s }$ mod $M ( M \leq 1 0 ^ { 9 } )$ 的最大值。  

# 题解  

由于我们暴力 $\mathrm { O } ( 2 ^ { 2 N } )$ 做能接受的最坏 $N$ 正好是实际 $N$ 的一半，所以不妨考虑折半搜索。我们将一条路径拆成前 $N - 1$ 步和后 $N - 1$ 步，那么这两部分是对称的且最终在网格图的斜对角线上相交构成一条完整的路径。  

于是路径长度被折半，我们分别暴力枚举前后两部分的所有方案并记录下来，最后问题就变为，如何快速合并两半的方案并使得答案最大。考虑如果我们将到达斜对角线 $( n - x + 1 , x )$ 的前半部分的所有方案的 $s$ 记录在数组 $F _ { x }$ 中，后半部分的所有方案的 $\boldsymbol { S }$ 记录在数组 $G _ { x }$ 中，那么问题就变为：求$\operatorname* { m a x } _ { a , b } ( ( F _ { x , a } \times 1 0 ^ { N } + G _ { x , b } )$ mod $m$ ）  

不妨令所有 $F _ { x , a } \gets F _ { x , a } \times 1 0 ^ { N }$ 并将 $F _ { x } , G _ { x }$ 升序排序，那么我们可以用双指针线性求出对所有 $F _ { x , a }$ ，最大的 $G _ { x , b }$ 满足 $F _ { x , a } + G _ { x , b } < M$ 是什么，这样二者匹配一定最优。还有一种可能是和超过 $M$ 但一定不超过 $2 M$ ，此时一定是选择两数组各自最大的元素匹配最优。  

Code  

using namespace std;   
const int $N = 2 \textcircled { 2 }$   
int n,m,a[N][N];   
vector<int>f1[N],f2[N];   
nain()   
scanf("%d%d",&n,&m);   
for(int $i = 0$ ；i<n; $+ + \mathbf { i }$ A for(int j=0;j<n;++j) scanf("%d",&a[i][j]);   
for(int i=0;i<(1<(n-1));++i)   
{ int $x = \scriptstyle \ 1 - 1 , y = \pmb { \Pi } - 1$ ,bs $\mathbf { \tau } = \mathbf { \hat { 1 } }$ ,res=0; for(int j=0;j<n-1;++j) { res=(res+a[x][y]\*1ll\*bs)%m; bs=bs\*1011%m; if((i>>j)&1)y--; else x--; } res=(res+a[x][y]\*1ll\*bs)%m; f2[y].push_back(res);   
}   
int $6 5 = 1$ ：   
for(int i=0;i<n;++i) 2号 $6 5 { = } 6 5 ^ { \circ } 1 9 1 1 \%$ _   
for(int $\bar { \mathbf { 1 } } { = } \Theta ; \bar { \mathbf { 1 } } { < } ( 1 { < } { < } ( \mathfrak { n } { - } 1 ) ) \mathbf { 3 } { \div } 4 + \bar { \mathbf { 1 } } )$   
{ int $x = \theta , y = \theta , r \in 5 = \theta ,$ for(int $\dot { \beth } = \dot { \Theta }$ ;j<n-1;++j) { res=(res\*10ll+a[x][y])%m; if((i>>j)&1) y++; else x++; } f1[y].push_back(res\*1ll\*bs%m);   
}   
int ans $= \Theta$ ：   
for(int $\underline { { \boldsymbol { \mathsf { i } } } } = \boldsymbol { \mathsf { E } } .$ ;i<n; $+ + \dot { 1 }$ 一   
{ sort(f1[i].begin(),f1[i].end()); sort(f2[i].begin(),f2[i].end()); int len1 $\mathbf { \sigma } =$ (int)f1[i].size(); int len2 $\ O =$ (int)f2[i].size(); for(int j=0,k=len2-1;j<len1; $+ +  j$ ， { while(k>=0&&f2[i][k]+f1[i][: if( $k ^ { 2 } = 0$ ）ans $\mathbf { \lambda } =$ max(ans,f1[i][:  

ans $\mathbf { \lambda } =$ max(ans,f1[i][len1-1]+f2[i][len2-1]-m); } printf("%d\n",ans); return 0;  

# 题目大意  

有 $T ( T \leq 1 0 ^ { 5 } )$ 次询问，每次询问给定 $N , M , A , B _ { 1 } , B _ { 2 } ( N , M \leq 1 0 ^ { 6 } )$ 求  

$$
\sum _ { k = 0 } ^ { N - 1 } \left( ( A k + B _ { 1 } ) \mathrm { m o d } M \right) \left( \left( A k + B _ { 2 } \right) \mathrm { m o d } M \right)
$$  

# 题解  

前置知识：类欧几里得算法。  

令 $\begin{array} { r } { f ( a , b , n , \underset { \circ } { m } ) = \sum _ { i = 0 } ^ { n } \left\lfloor \frac { a i + b } { m } \right\rfloor , g ( a , b , n , m ) = \sum _ { i = 0 } ^ { n } i \left\lfloor \frac { a i + b } { m } \right\rfloor , h ( a , b , n , m ) , } \end{array}$ )= $\textstyle \sum _ { i = 0 } ^ { n } \left\lfloor { \frac { a i + b } { m } } \right\rfloor ^ { 2 }$ 则三者均可通过类欧算法 $\mathrm { O } ( \log m )$ 求出。则  

$$
\begin{array} { r l } { { } } & { { \displaystyle \sum _ { k = 0 } ^ { N - 1 } \left\{ ( A k + B _ { 1 } ) \bmod M \right\} \left\{ ( A k + B _ { 2 } ) \bmod M \right\} } } \\ { { } } & { { = \displaystyle \sum _ { k = 0 } ^ { N - 1 } \left( ( A k + B _ { 1 } ) - M \left\lfloor \frac { A k + B _ { 1 } } { M } \right\rfloor \right) \left( ( A k + B _ { 2 } ) - M \left\lfloor \frac { A k + B _ { 2 } } { M } \right\rfloor \right) } } \\ { { } } & { { = \displaystyle \sum _ { k = 0 } ^ { N - 1 } ( A k + B _ { 1 } ) ( A k + B _ { 2 } ) - M \displaystyle \sum _ { k = 0 } ^ { N - 1 } ( A k + B _ { 1 } ) \left\lfloor \frac { A k + B _ { 2 } } { M } \right\rfloor - M \displaystyle \sum _ { k = 0 } ^ { N - 1 } ( A k + B _ { 2 } ) } } \end{array}
$$  

可分为三类分别求解，其中前两项直接拆开就是 $f , g , h$ 和 $0 , 1 , 2$ 次幂和的若干组合乘积。我们重点关注最后一项。  

一个显然的观察是 $\textstyle \left\lfloor { \frac { A { \bar { k } } + B _ { 1 } } { M } } \right\rfloor$ 和 $\textstyle \left\lfloor { \frac { A k + B _ { 2 } } { M } } \right\rfloor$ 至多相差一，不妨假设 $B _ { 1 } \leq B _ { 2 }$ ，则我们可以把$\textstyle \sum _ { k = 0 } ^ { N - 1 } \left\lfloor { \frac { A k + B _ { 1 } } { M } } \right\rfloor \left\lfloor { \frac { A k + B _ { 2 } } { M } } \right\rfloor$ 著时近为 $\textstyle \sum _ { k = 0 } ^ { N - 1 } \left\lfloor { \frac { A k + B _ { 2 } } { M } } \right\rfloor ^ { 2 }$ 则相差的分  
$\begin{array} { r } { \sum _ { k = 0 } ^ { N - 1 } \lfloor \frac { A k + B _ { 2 } } { M } \rfloor \big ( \lfloor \frac { A k + B _ { 2 } } { M } \rfloor - \lfloor \frac { A k + B _ { 1 } } { M } \rfloor \big ) } \end{array}$ ，其中 $\textstyle { \left\lfloor { \frac { \bar { A } k + \bar { B } _ { 2 } } { M } } \right\rfloor } - \left\lfloor { \frac { A k + B _ { 1 } } { M } } \right\rfloor$ 要么只能为0或1。关注令 $\left\lfloor { \frac { A k + B _ { 2 } } { M } } \right\rfloor$ 取值一致的 $k$ 的区间范围，即当 $d _ { 2 , c } \leq k < d _ { 2 , c + 1 }$ 时有 $\begin{array} { r } { \lfloor \frac { A k + B _ { 2 } } { M } \rfloor = c } \end{array}$ ，其中（204号 $\begin{array} { r } { d _ { 2 , c } = \operatorname* { m i n } \left( N , \lceil \frac { c M - B _ { 2 } } { A } \rceil \right) } \end{array}$ ，同理我们也能定义对应的 $d _ { \mathrm { 1 s } }$ （20  
求出 $c$ 的上界 $\begin{array} { r } { X = \left\lfloor \frac { A ( N - 1 ) + B _ { 2 } } { M } \right\rfloor } \end{array}$ 于是  

$$
\begin{array} { r l } & { \quad \displaystyle \sum _ { k = 0 } ^ { N } \left\lfloor \frac { A k + B _ { 2 } } { \mathcal { M } } \right\rfloor \left( \left\lfloor \frac { A k + B _ { 2 } } { \mathcal { M } } \right\rfloor - \left\lfloor \frac { A k + B _ { 1 } } { \mathcal { M } } \right\rfloor \right) } \\ & { = \displaystyle \sum _ { c = 0 } ^ { N } c ( d _ { 1 , c } - d _ { 2 , c } ) } \\ & { - \displaystyle \sum _ { c = 0 } ^ { N - 1 } ( d _ { 1 , c } - d _ { 2 , c } ) + X ( d _ { 1 , x } - d _ { 2 , x } ) } \\ & { = \displaystyle \sum _ { c = 0 } ^ { N } c \left( \left\lfloor \frac { c d } { \mathcal { M } } - \frac { B _ { 1 } } { \mathcal { M } } \right\rfloor - \left\lfloor \frac { c d } { \mathcal { M } } - \frac { B _ { 2 } } { \mathcal { M } } \right\rfloor \right) + X ( d _ { 1 , x } - d _ { 2 , X } ) } \\ & { \quad - \displaystyle \sum _ { c = 0 } ^ { N - 1 } c \left( \left\lfloor \frac { c d + A - 1 - D _ { 1 } } { A } \right\rfloor - \left\lfloor \frac { c d + A - 1 - B _ { 2 } } { A } \right\rfloor \right) + X ( d _ { 1 , x } - d _ { 2 , X } ) } \\ & { = \displaystyle \sum _ { c = 0 } ^ { N } c \left( \left\lfloor \frac { c d + A - 1 - D _ { 1 } } { A } \right\rfloor - \left\lfloor \frac { c d + A - 1 - D _ { 2 } } { A } \right\rfloor \right) + X ( d _ { 1 , x } - d _ { 2 , X } ) } \end{array}
$$  

于是又拆成了能利用 $f , g , h$ 求解的形式。总时间复杂度为 $\mathrm { O } ( { \cal T } \log M )$  

一些细节：  

·虽然答案不会超过longlong范围，但是求解的过程中是有可能的，故需要开__int128中 $A - 1 - B _ { i }$ 可能为负数，不过由于是二者相减故我们可以给前后同时加上一个 $t . A$ 来保证 $t A +$ $A - 1 - B _ { i } \geq 0$ 而答案不会改变。  

Code  

using namespace std;   
inline int read()   
{ int $a n s = \theta , f = 1$ ： char $c =$ getchar(); while $( ( \Sigma ^ { \circ } \ni \ P \ | \ | \ \mathbb { C } \ll \ ^ { \circ } \Theta ^ { \circ } ) \{ \underline { { \mathbb { i } } } \ f ( \mathbb { C } = = \ ^ { \circ } \_ { - } \cdot \ ^ { \circ } ) \ f = - 1 \} \mathbb { C } = \underline { { \mathbb { g } } } \in \mathbb { C } \mathbb { C } \lceil \mathsf { c h a r } ( \blacktriangledown ) \frac { : } { : } \}$ while $\angle C > = 9 0 ^ { \circ }$ ){ans $\underline { { \underline { { \mathbf { \Pi } } } } } =$ (ans<<1)+(ans<<3)+c-'0'; $c =$ getchar();} return ans\*f;   
}   
inline void write(int x)   
{ if(x<0） putchar('-'),x=-x; if(x/10) write(x/10); putchar((char)(x%10)+'0');   
}   
const int $N = 1 \div 5 + 5$ ：   
int t,n,m,a,b1,b2;   
struct node   
{ int f,g,h;   
}；   
node F(int a,int b,int m,int n)   
{ if( $\scriptstyle \mathbf { \overrightarrow { n } } = = \mathbf { \overrightarrow { 0 } }$ ）return (node){0,0,0}； int $A = \exists / \mathrm { m } , \mathsf { E } { = } \mathsf { b } / \mathrm { m } ;$ int $\mathbb { P 1 } = \bar { \boldsymbol { \Pi } } + \bar { \boldsymbol { \mathrm { 1 } } }$ ${ \mathsf { P } } \bar { \mathsf { Z } } = { \mathsf { n } } ^ { \ast } { \left( { \mathsf { n } } + \bar { \mathsf { 1 } } \right) } / \bar { \mathsf { Z } } .$ int $\mathsf { P 3 } \mathrm { = } \Pi ^ { \ast } ( \mathsf { n + 1 } ) ^ { \ast } ( 2 ^ { \ast } \mathsf { n + 1 } ) / 6 ;$ $\operatorname { i f } ( \ a - \operatorname { m } \vert \\vert \ b \geq \operatorname { m } )$ { node $\mathsf { r e s } = \mathsf { F } ( \mathsf { a } ^ { \mathsf { g } } \mathsf { a m } , \mathsf { b } ^ { \mathsf { g } } \mathsf { a } ^ { \mathsf { m } } , \mathsf { m } , \mathsf { n } ) .$ . int $\bar { \mathsf { f } } { = } \mathsf { P } 2 ^ { { \ast } } \mathbb { A } { + } \mathsf { P } 1 ^ { { \ast } } \mathbb { E } { + } \mathsf { r } \in \mathbb { S } , \bar { \mathsf { f } } ;$ int $\mathbf { g } = \mathbf { P } 3 ^ { * } \mathbb { A } + \mathbf { P } 2 ^ { * } \mathbb { E } + \Gamma \in { \mathbb { S } } \cdot \mathbf { g } :$ int h=2\*B\*res.f+2\*A\*res.g+P3\*A\*A+P1\*B\*B+2\*P2\*A\*B+res.h; return (node){f,g,h}; } int $k { = } \left( a ^ { \mathrm { { s } } } \mathfrak { n } { + } b \right) / \mathfrak { m } _ { \mathrm { { i } } }$ node $\Gamma \mathsf { e } \mathsf { s } = \mathsf { F } ( \mathsf { m } , \mathsf { m } - \mathsf { b } - 1 , \mathsf { a } , \mathsf { k } - 1 )$ ： int f=n\*k-res.f; int $\underline { { \mathbb { g } } } = ( \lvert \mathrm { k } ^ { \mathrm { s } } \rvert \Pi ^ { \mathrm { s } } \left( \Pi + 1 \right) - \mathsf { r } \mathsf { e } \mathbb { s } \mathrm { ~ . ~ } \mathsf { h } - \mathsf { r } \mathsf { e } \mathbb { s } \mathrm { ~ . ~ } \mathsf { f } ) / 2 \mathrm { ; ~ }$ int $\mathsf { h } { = } \mathsf { n } ^ { \ast } \mathsf { k } ^ { \ast } ( \mathsf { k } { + } 1 ) { - } 2 ^ { \ast } \mathsf { r } ^ { \ast } \mathsf { e } 5 \cdot \mathsf { g } { - } 2 ^ { \ast } \mathsf { r } \mathsf { e } 5 \cdot \mathsf { f } - \mathsf { f } ;$ return (node){f,g,h};   
t=read();   
while(t--)   
{ n=read()-1; m=read(); $\tilde { \mathbf { a } } =$ read();b1=read();b2=read(); if( $\widetilde { \mathsf { a } } = = \widetilde { \mathsf { b } } \widetilde { \mathsf { \Omega } } .$ { write( $( n + 1 ) ^ { * } 6 1 ^ { * } 6 2$ );puts(""); continue; } 讠 $F ( 6 1 ) = 6 2$ ）swap(b1,b2); int ans $1 = 0$ ,ans $z = \Theta$ ,ans3=0; //- -ans1 ans1 $\boldsymbol { \mathsf { t } } = \boldsymbol { \mathfrak { Q } } ^ { \ast } \boldsymbol { \bar { \mathfrak { Q } } } ^ { \ast } \boldsymbol { \Pi } ^ { \ast } ( \boldsymbol { \mathsf { n } } + \boldsymbol { \mathsf { 1 } } ) ^ { \ast } ( 2 ^ { \ast } \boldsymbol { \mathsf { n } } + \boldsymbol { \mathsf { 1 } } ) / 6 \boldsymbol { \mathsf { ; } }$ ans1 $\scriptstyle \pm = \Xi ^ { \pm } ( \log 1 + \log 2 ) ^ { \pm } \Pi ^ { \pm } ( \bar { \Pi } + 1 ) / 2 .$ ans1 $\scriptstyle + = 6 1 ^ { * } [ 6 2 ^ { * } ( \ n + 1 )$ ： //- -ans2 node $\mathsf { F 1 } = \mathsf { F } \left( \mathsf { a , b 1 , m _ { \mathsf { 1 } } } \mathsf { n } \right) , \mathsf { F 2 } = \mathsf { F } \left( \mathsf { a , b 2 , m _ { \mathsf { 1 } } } \mathsf { n } \right) .$ 日 $1 1 5 . 2 + = a ^ { \ast } F 2 . 8 + b 1 ^ { \ast } F 2 . 6 .$ - $\mathtt { a m s 2 + = a ^ { \pm } F 1 . g + b 2 ^ { \pm } F 1 . f _ { \perp } }$ ans $2 ^ { 3 5 } = m$ ： / -ans3 ans $3 = F 2 . h$ ： int $m \cdot = ( a ^ { \ast } \cdot n + b 2 ) / m ;$ 2号 ans3- $= n n ^ { \ast }$ (min( $\boldsymbol { \Pi } { + } \mathbf { 1 }$ (nn\*m-b1+a-1)/a)-min(n+1,(nn\*m-b2+a-1)/a)); int tmp $= 6 . 2 / z$ ： b1=a-b1-1+a\*tmp; $b 2 = a - b 2 - 1 + a ^ { 3 }$ tmp; node $F 3 = F$ (m,b1,a,nn-1), $F _ { 4 } = F$ (m,b2,a,nn-1); ans3-=F3.g-F4.g;ans3\*=m\*m; write(ans1-ans2+ans3);puts("");   
}   
return 0;  