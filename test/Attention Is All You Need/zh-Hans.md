> 原文：https://arxiv.org/pdf/1706.03762
> 翻译：https://hackmd.io/@shaoeChen/BkxGXkS96

## Abstract

主流的序列转换模型都是基于复杂的recurrent或是convolutional neural networks，不管那一个都包着一个encoder与一个decoder。效能最好的模型通常是透过一个注意力机制来连结encoder与decoder。我们提出一个新的简单的网路架构，也就是Transformer，完全的基于注意力机制，完全没在管recurrence与convolutions的。在两个机器翻译任务上就说明着，这些模型在质量方面有着更好的效果，同时更为平行化，训练时间明显更少。我们的模型在WMT 2014英语-德语翻译任务上达到28.4 BLEU，超过目前已知的最佳结果(包含ensembles, by over 2 BLEU)。在WMT 2014英语-德语翻译任务中，经过3.5天在八张GPUs上的训练之后，我们的模型建立一个新的哩程，单一模型，41.8的BLEU score，这只是目前文献中已知的最佳模型一小部份的训练成本。我们透过将Transformer成功地应用到具有大量且有限的训练资料的English constituency parsing来说明它可以很好地泛化到其它的任务上。

### 1 Introduction

Recurrent neural networks、long short-term memory \[13\]与gated recurrent \[7\] neural networks，已经稳稳地在序列模型与 [转导](https://terms.naer.edu.tw/detail/20616afa224a0100be532fb61dbb022a/) 问题上目前最好的方法(像是语言模型与机器翻译\[35, 2, 5\])。后续众多努力持续着突破递回语言模型与编码器-解码器架构的天花板。

递回模型通常通常会沿着输入与输出序列的符号位置做因子计算(factor computation)。将位置与计算时间中的步骤(step)切齐，它们生成一系列的隐藏状态 $h_{t}$ ，作为先前的隐藏状态 $h_{t - 1}$ 的函数与位置 $t$ 的输入。这种固有的顺序性质在本质上就阻碍了训练样本的平行化，这在一些比较长的序列长度情况下变的重要，因为记忆体约束就卡住了样本间的批处理。近来的研究透过 [因子分解](https://terms.naer.edu.tw/detail/1eb27f165a2a57c0f748945614145953/) 技巧与条件计算明显的提高了计算效率，同时也提高后者的模型效能。不过啊，这有顺序的计算的先天限制还是在的。

注意力机制俨然成为各种任务中引人注目的序列建模与转导模型不可或缺的一部份，它允许对其依赖关系建模，而不需要考虑到它们在输入或是输出序列中的距离。然而，除了少数情况外，这类的注意力机制都是跟递回网路结合使用的。

在这个研究中，我们提出Transformer，这是一种避免递回的模型架构，并且完全依赖注意力机制来绘制出输入与输出之间的全域依赖关系。Transformer可以明显地更加的平行化，而且可以在训练品质上来到一个新的境界(只要你有8张P100，简单的训练12小时就可以)。

### 2 Background

减少顺序计算(sequential computation)的目标也构成Extended Neural GPU、ByteNet、ConvS2S的基础，它们都是用卷积神经网路来做为基础的建构区块，以平行的方式计算所有输入与输出位置的隐藏表示(hidden representations)。在这些模型中，关联两个任意输入或输出位置的信号所需的运算数量会随着位置之间的距离而增加，ConvS2S是线性增加，ByteNet则是对数增长。这让学习位置比较遥远的输出入之间的依赖关系变的更加困难。在Transformer中，这问题已经被减化成常数数量的操作，尽管这个代价是由于我们平均注意力权重位置(attention-weighted positions)而降低有效解析度，不过这问题我们会用Multi-Head Attention来抵消(见Section 3.2说明)。

Self-attention(自注意力)，有时候称为intra-attention，是一种为了计算序列的表示而将单一序列相关联的注意力机制。Self-attention已经被成功地的应用在各种任务中，包括 [阅读理解](https://terms.naer.edu.tw/detail/4f4ca5c561c98006e991be54584e0d85/) ，抽象摘要、文字蕴涵以及跟学习任务无关的句子表示。

End-to-end memory networks基于递回注意力机制，而非sequencealigned recurrence，而且已经被证明在简单的语言问答与语言建模任务上表现的不错。

然而，据我们所知，Transformer是第一个完全依赖self-attention在不使用序列对齐的RNNs或是卷积来计算其输入与输出的计算表示的转导模型。接下来的章节中，我们将会说明Transformer、激发self-attention并讨论相对于其它模型的优势。

## 3 Model Architecture

多数竞争性的神经序列转导模型都有一个encoder-decoder的结构。encoder将符号表示的输入序列 $\left(\right. x_{1} , . . . , x_{n} \left.\right)$ 映射到一个连续表示的序列 $\mathbf{z} = \left(\right. z_{1} , . . . , z_{n} \left.\right)$ 。给定 $\mathbf{z}$ ，然后decoder会每次生成出一个符号输出序列 $\left(\right. y_{1} , . . . , y_{n} \left.\right)$ 的元素。每个步骤中，模型都是auto-regressive，然后在生成下一个的时候将前一个生成的符号当做附加的输入。

Transformer依循着下面这个架构，在encoder跟decoder都使用者堆叠的self-attention与point-wise、fully connected layers，分别如Figure 1左右图所示。

![image](https://hackmd.io/_uploads/HkHGrYDc6.png)

### 3.1 Encoder and Decoder Stacks

**Encoder:** encoder是由 $\text{N} = 6$ 个相同层堆叠所组成。每一层都有两个子层。第一个是多头注意力机制(multi-head self-attention mechanism)，第二个比较简单，position-wise fully connected feed-forward network。两个子层之间我们采用residual connection，接下来就是layer normalization。也就是说，每个子层的输出会是 $\text{LayerNorm} \left(\right. x + \text{Sublayer} \left(\right. x \left.\right) \left.\right)$ ，其中 $\text{Sublayer} \left(\right. x \left.\right)$ 是由子层本身所实现的函数。为了方便这些子层的连接，模型中的所有子层以及嵌入层(embedding layers)都会产生 $d_{\text{model}} = 512$ 的维度输出。

**Decoder:** decoder也是由 $\text{N} = 6$ 个相同层堆叠所组成。不过它除了两个子层之外还插入第三个子层，这个子层会对encoder stack的输出做多头注意力的处理。类似于encoder，我们会在每个子层之间使用residual connection，接着就是layer normalization。我们也同时调整decoder stack中的自注意力子层(self-attention sub-layer)，以防止位置(position)关注后续的位置。这种遮罩跟输出嵌入偏移一个位置的真实相结合的作法，确保了位置 $i$ 的预测就只能依赖于小于 $i$ 的已知输出。

这边说的就是，总之，一开始就只有第一个字看的到，其它不给看，然后给看第一、第二个字，其它不给看，大概有一种dropout的概念，不过是有序的遮掉。

### 3.2 Attention

注意力函数(attention function)可以将之视为将query与key-value pairs映射到输出的概念，其中query、key、values与output都是向量。输出(output)是值(values)的加权和，其中分配给每个值(value)的权重是透过查询(query)与相对应键(key)的相容性函数（compatibility function)计算而得。

#### 3.2.1 Scaled Dot-Product Attentio

我们把我们的特别注意力层称为"Scaled Dot-Product Attention"(Figure 2)。input包含了维度为 $d_{k}$ 的查询(queries)与键(keys)，以及维度为 $d_{v}$ 的值(values)。我们计算查询(query)与所有键(keys)的点积，除上 $\sqrt{d_{k}}$ ，然后做softmax的处理来得到值(values)的权重。

![image](https://hackmd.io/_uploads/rklklz556.png)

Figure 2: (left) Scaled Dot-Product Attention. (right) Multi-Head Attention consists of several attention layers running in parallel.

实务上，我们会同时计算一组的查询(queries)，会将之打包成一个矩阵 $Q$ 。键(keys)与值(values)也会分别打包成矩阵 $K$ 与 $V$ 。我们计算的输出矩阵如下：

$$
(\text{1}) \text{Attention} \left(\right. Q , K , V \left.\right) = \text{softmax} \left(\right. \frac{Q K^{T}}{\sqrt{d_{k}}} \left.\right) V
$$

两个最常用的注意力函数为additive attention与dot-product (multiplicative) attention。除了缩放因子 $\frac{1}{\sqrt{d_{k}}}$ 之外，dot-product attention跟我们的演算法是一样的。additive attention则是用具有单一隐藏层的前馈网路来计算相同性函数。尽管两种方法的理论复杂度是一样的，不过实务上dot-product attention还是快多了，因为它可以用高度最佳化的矩阵乘法来实现。

虽然对于较小的 $d_{k}$ 来说，这两个机制的表现是类似的，不过在没有较大的缩放值 $d_{k}$ 的情况下，additive attention是比dot product attention还要好的。我们是这样怀疑的，较大的 $d_{k}$ 会造成点积的值变的非常的大，这也将softmax function梯度极小的区域。为了抵消这个影响，我们才会选择用 $\frac{1}{\sqrt{d_{k}}}$ 来做缩放。

这边说明为什么点积会变大的原因，假设 $q$ 与 $k$ 的成份(components)是均值为0且方差为1的independent random variables。那它们的点积 $q \cdot k = \sum_{i = 1}^{d_{k}} q_{i} k_{i}$ ，均值就是0，方差就会是 $d_{k}$

#### 3.2.2 Multi-Head Attention

如果说不要用单一个attention function($d_{\text{model}}$ 维的keys、values、queries)，我们发现到这对于将queries、keys与values分别用不同的学习到的线性投影 $h$ 次到 $d_{k} , d_{k} , d_{v}$ 维上是有帮助的。在这些投影后的queries、keys与values的每个版本上，我们会平行执行注意力函数，然后生成 $d_{v}$ 维的输出值。把它们连结起来然后再次的投影，产出最终的值，如Figure 2所示。

![image](https://hackmd.io/_uploads/rkX1K7qc6.png)

Figure 2: (left) Scaled Dot-Product Attention. (right) Multi-Head Attention consists of several attention layers running in parallel.

Multi-head attention允许模型可以共同关注来自不同的位置不同的表示子空间中的信息。single attention head情况下，平均会抑制这种情况。

$$
\text{MultiHead} \left(\right. Q , K , V \left.\right) = \text{Concat} \left(\right. \text{head}_\text{1} , . . . , \text{head}_{h} \left.\right) W^{O} \\ \text{where head}_{i} = \text{Attention} \left(\right. Q W_{i}^{Q} , K W_{i}^{K} , V W_{i}^{V} \left.\right)
$$

其中投影是参数矩阵 $W_{i}^{Q} \in \mathbb{R}^{d_{\text{model}} \times d_{k}}$, $W_{i}^{K} \in \mathbb{R}^{d_{\text{model}} \times d_{k}}$, $W_{i}^{V} \in \mathbb{R}^{d_{\text{model}} \times d_{v}}$ 与 $W^{O} \in \mathbb{R}^{h d_{v} \times d_{\text{model}}}$

在这个研究中，我们采用的是 $h = 8$ 个平行注意力层(layers)，或头(heads)。这八个每一个我们都使用 $d_{k} = d_{v} = d_{\text{model}} / h = 64$ 。由于每一个head的维度降低了，总计算成本跟full dimensionality的single-head attention是差不多的。

#### 3.2.3 Applications of Attention in our Model

Transformer以三种不同的方法来用着multi-head attention：

- 在"encoer-decoder attention" layers中，queries来自前一个decoder layer，keys与values则是来自于encoder的输出。这让decoder中的每个位置都可关注input sequence中的所有位置。这模仿了sequence-to-sequence models中的encoder-decoder attention mechanisms。
- encoder包含self-attention layers。在self-attention layer中，所有的keys、values与queries都是来自相同的位置(place)，这种情况下就是encoder前一层的输出。encoder中的每个位置能够关注encoder前一层中的所有位置。
- 类似地，decoder中的self-attention layers允许decoder中的每一个位置关注decoder中截至该位置(包含)的所有位置。为了保留auto-regressive的性质，我们需要预防decoder中的向左信息流动。我们通过在 scaled dot-product attention中屏蔽(设定为 $\infty$)所有对应非法连接的softmax输入值来实现这一点。见Figure 2。

### 3.3 Position-wise Feed-Forward Networks

除了attention sub-layers之外，我们的encoder与decoder中的每一层都包含一个fully connected feed-forward network，单独且相同地在每个位置应用。这包含两个线性转换，中间则使用ReLU。

$$
(\text{2}) \text{FFN} \left(\right. x \left.\right) = max \left(\right. 0 , x W_{1} + b_{1} \left.\right) W_{2} + b_{2}
$$

尽管不同位置间的线性转换是相同的，层到层之间仍然是使用不同的参数。另一种描述这种作法的方式就是想成就两个1x1的卷积。输入与输出的维度 $d_{\text{model}} = 512$ ，中间层的维度则是 $d_{f f} = 2048$ 。

### 3.4 Embeddings and Softmax

类似于其它序列转导模型，我们使用学习的嵌入(learned embeddings)将输入与输出的token转换为 $d_{\text{model}}$ 维的向量。我们也使用通常的学习线性转换函数与softmax函数将decoder的输出转换成预测next-token的机率。在我们的模型中，两个embedding layers与pre-softmax linear transformation之间会共享相同的权重矩阵。在嵌入层(embedding layers)中，我们会以 $\sqrt{d_{\text{model}}}$ 乘上权重。

### 3.5 Positional Encoding

因为我们的模型并不包含递回与卷积，为了让模型能够用上序列的顺序，我们必需要注入这些tokens在序列中的绝对或相对位置的信息。为此，我们把"positional encodings"加到encoder与decoder堆叠底部的input embeddings。positional encodings跟embeddings有相同的维度， $d_{\text{model}}$ ，也因此两个矩阵可以相加。positional encodings有很多种选择，有学习来的，也有固定的。

在这个研究中，我们使用不同频率的sine与cosine函数：

$$
\begin{aligned}
PE_{(pos, 2i)} &= \sin\left(\frac{pos}{10000^{2i / d_{\text{model}}}}\right) \\
PE_{(pos, 2i + 1)} &= \cos\left(\frac{pos}{10000^{2i / d_{\text{model}}}}\right)
\end{aligned}
$$

其中 $p o s$ 指的是位置， $i$ 指的是维度。也就是说，位置编码(positional encoding)的每个维度都对应于正弦曲线。波长形成一个从 $2 \pi$ 到 $10000 \cdot 2 \pi$ 的几何级数。选择这个函数是因为我们假设它可以让模型简单地透过相对位置学习到关注，因为对于任意固定偏移量 $k$ 来说， $P E_{p o s + k}$ 可以表示为 $P E_{p o s}$ 的线性函数。

我们也实验过使用学习的positional embeddings，有发现到这两种版本的所产生的结果非常相近(见Table 3 row (E))。我们选择使用正弦版本(sinusoidal version)是因为它可以推断出比训练期间所遇到的序列长度还要再长的序列长度。

![image](https://hackmd.io/_uploads/HkmEGM09p.png)

## 4 Why Self-Attention

这一节中，我们要来把self-attention layers跟各种的recurrent与convolutional layers好好的比一比，这些常用层常见用于将符号表示的一个variable-length sequence $\left(\right. x_{1} , . . . x_{n} \left.\right)$ 映射到另一个相同长度的序列 $\left(\right. z_{1} , . . . , z_{n} \left.\right)$ ，其中 $x_{i} , z_{i} \in \mathbb{R}^{d}$ ，就像典型的序列转导编码器或解码器中的隐藏层。在使用self-attention的部份我们考虑三个必要条件。

一个就是每一层的总计算复杂度。另一个就是可以平行化的计算量，利用所需要的最小序列操作数量来衡量。

第三个就是网路中长期相依性(long-range dependencies)之间的路径长度(path length)。学习长期相依性在很多序列转导任务中是一个关键挑战。影响学习这种相依性能力的关键因子就是路径(path)的前馈(forward)与反馈(backward)信号在网路中必需经过的路径长度。愈短就愈容易学到长期相依性。所以啊，我们还比较了不同层所组成的网路中任意两个输入与输出位置之间最长的路径长度。

如Table 1所注记，self-attention layer是以固定数量按序执行操作连接所有位置，而recurrent layer则是需要 $O \left(\right. n \left.\right)$ 。在计算复杂度的部份，当序列长度 $n$ 小于表示维度 $d$ 的时候，self-attention layers就会比recurrent layers来的快，这见于机器翻译中最好的模型所使用的sentence representations(语句表示)，如word-piece与byte-pair的表示。为了提高涉及超长语句的任务的计算效能，self-attention可以限制单纯的考虑输入序列中围绕于相对应输出位置中心的大小为 $r$ 的邻域。这将使最大路径长度增加为 $O \left(\right. n / r \left.\right)$ 。我们计划在未来研究中进一步研究这个方法。

![image](https://hackmd.io/_uploads/HJ4ECLJoa.png)

kernel宽度 $k < n$ 的单一卷积层无法连接所有的输入与输出成对的位置(两两无法全部相接)。在contiguous kernels的情况下要全部接上线的话就必需要堆 $O \left(\right. n / k \left.\right)$ 个卷积层，在dilated convolutions的话则是需要 $O \left(\right. l o g_{k} \left(\right. n \left.\right) \left.\right)$ 个卷积层，用这样的方式来增加网路中任意两个任置之间的最长路径的长度。卷积层的计算复杂度通常比递回层贵个 $k$ 倍吧。不过啊，Separable convolutions通常可以将复杂度降低到 $O \left(\right. k \cdot n \cdot d + n \cdot d^{2} \left.\right)$ 。即使 $k = n$ ，separable convolution的复杂度也就只是等价于self-attention layer与 point-wise feed-forward layer的结合，这也是我们模型中所采用的方法。

做为附带好处，self-attention可以产生更多可解释模型。我们从我们的模型中检查注意力分布，并且在附录中说明与讨论。不仅个别的attention head明显学会执行不同的任务，许多attention heads似乎还表现出与句子的文法和语义结构相关的行为。

## 5 Training

这边来玩玩我们的模型训练制度。

### 5.1 Training Data and Batching

我们的训练资料集是标准WMT 2014 English-German dataset，这包含大约450万对语句(英文到德语的语句)。语句的部份用byte-pair encoding，这个encoding具有37000个tokens的共享来源-目标的词汇。对于English-French的部份，我们使用更大的WMT 2014 English-French dataset，包含36M对句子，并且将tokens拆分为32000 word-piece vocabulary。差不多长度的语句就会分批放在一起。每个训练批次包含一组的sentence pairs，大概有25000个source tokens与25000个target tokens。

### 5.2 Hardware and Schedule

我们在一台装有8张NVIDIA P100 GPUs的电脑上训练模型。对于我们论文中所述的基本模型的超参数，每个训练step大概需要0.4秒。这个基本模型大概训练了100,000个steps或12小时。大一点的模型的话(Table 3最后一行说的那个)，每个step要1秒。总共训练300,000个steps(3.5天)。

### 5.3 Optimizer

我们使用Aadm optimizer，参数的部份 $\beta_{1} = 0.9 , \beta_{2} = 0.98$ 且 $\epsilon = 10^{- 9}$ 。我们根据下面的数学式在训练过程中改变learning rate：

$$
(\text{3}) l r a t e = d_{\text{model}}^{- 5} \cdot min \left(\right. s t e p_{n u m}^{- 0.5} , s t e p_{n u m} \cdot w a r m u p_{s} t e p s^{- 1.5} \left.\right)
$$

这对应于第一个warmup\_steps training steps的learning rate线性增长，接着以step number的平方根倒数按比例地减少。warmup\_steps=4000。

### 5.4 Regularization

我们在训练期间使用了三种正规化类型：

- **Residual Dropout** 我们在每个sub-layer的输出上使用dropout，然后再加到sub-layer的输入并且正规化。此外，我们还在encoder与decoder的堆叠中的embedding与positional encodings的总和中使用dropout。基本模型的部份，我们使用 $P_{d r o p} = 0.1$ 。
- **Label Smoothing** 训练期间，我们使用 $\epsilon + l s = 0.1$ 的值来做label smoothing。这虽然会降低困惑度，因为模型的学习会变的更加不确定，不过这可以增加准确度与BLEU score。

perplexity，困惑度，这是度量语言模型的一种指标。

## 6 Results

### 6.1 Machine Translation

在WMT 2014 English-to-German的翻译任务上，big transformer model(Transformer (big) in Table 2)优于先前看过最好的模型(包含ensembles)有2.0 BLEU之多，建立了新的最佳28.4的BLEU score。模型的配置在Table 3的最后一行。在8张P100 GPUs上训练3.5天。尽管是基本模型也是碾压所有先前所发布的模型与集成模型(ensembles)，而且训练成本还只是任何一个竞争模型的一小部份而以。

![image](https://hackmd.io/_uploads/S19vAUyoa.png)

在WMT 2014 English-to-French任务上，大型模型的部份(big model)得到41.0的BLEU score，也是优于所有先前所发布的单一模型，而且训练成本不到他们的1/4。English-to-French的模型使用dropout为 $P_{d r o p} = 0.1$ ，而非 $0.3$

基本模型的部份，我们使用最后五个检查点(checkpoints)做平均得到单一模型(signle model)，这五个检查点是以10分钟的间隔来写入。大型模型的部份，我们平均最后20个检查点。我们使用 [定向搜索](https://terms.naer.edu.tw/detail/e80a9c57842994528399bc9186a4b39c/) (beam search)，beam size为4且length penalty $\alpha = 0.6$ 。这些超参数是在开发集上做实验后所选择的。我们把推论期间的最大输出长度设置为输入长度+50，不过可以的话会尽可能的提早终止。

Table 2总结我们的研究成果，并跟文献中的其它模型架构比较翻译品质与训练成本。我们透过乘上训练时间以及所使用的GPU数量跟每块GPU的sustained single-precision floating-point capacity的估测值来估测用于训练模型的浮点计算数。

### 6.2 Model Variations

为了评估Transformer不同组件的重要性，我们以不同的方式来改变基本模型，看看在newstest2013开发集上的English-to-German翻译效能上的改变。我们使用上一节所述的beam search，不过没有做检查点的平均。相关结果呈现于Table 3。

Table 3中的rows (A)，我们改变attention heads的数量以及attention key、value的维度，然后维持计算量不变，如Section 3.2.2所述。虽然single-head attention会比最佳化设定还要糟0.9 BELU，不过太多头(head)也是会造成品质降落。

Table 3中的rows (B)，我们观察到降低attention key的大小 $d_{k}$ 会伤到模型品质。这说明着确定相容性是不容易的，而且比点积更复杂的相容性函数说不定是有好处的。我们进一步的在©、(D)观察到，一如预期那般，模型愈大愈好，而且dropout对于避免过拟合非常有帮助。(E)的部份，我们用学习的位置嵌入(positional embedding)来取代sinusoidal positional encoding，我们观察到，所产生的结果与基本模型几无差异。

### 6.3 English Constituency Parsing

为了评估Transformer是否可以泛化至其它任务，我们在英文选区解析上做了实验。这个任务提出特别的挑战：输出受到强烈的结构约束，而且明显比输入长。此外，RNN sequence-to-sequence models并没有办法在小资料范例中得到最好的结果。

我们在Wall Street Journal (WSJ) portion of the Penn Treebank资料集上训练一个4-layer $d_{m o d e l} = 1024$ 的transformer，大概40K的训练语句。我们还在一个semi-supervised的环境中训练它(使用一个更大的高置信度与BerkleyParser语料库，大约17M的语句)。我们WSJ使用16K tokens的词汇，semi-supervised的环境中则是使用32K的词汇。

我们只有在Section 22开发集上做少量的实验来选择dropout、attention与residual(section 5.4)、learning rates与beam size，其它参数都跟English-to-German base translation model一样维持不变。推论过程中，我们将最大输出长度增加为输入长度+300。对于WSJ only与semi-supervised中使用beam size=21与 $\alpha = 0.3$ 的设置。

Table 4中的结果说明着，尽管没有做一些特别的调整，我们的模型效能却出乎意料之外的好，产生的结果比先前提过的所有模型都要来的好，除了Recurrent Neural Network Grammar。

![image](https://hackmd.io/_uploads/rJL2C8ysT.png)

跟RNN sequence-to-sequence models相比，尽管只有在40K的WSJ训练集上训练，Transformer还是优于BerkeleyParser。

## 7 Conclusion

在这个研究中，我们提出Transformer，第一个完全基于注意力的序列转导模型，用multi-headed self-attention取代掉encoder-decoder架构中常见的recurrent layers。

对于翻译任务而言，Transformer明显训练的比基于recurrent或convolutional layers的架构还要来的快。在WMT 2014 English-to-German与WMT 2014 English-to-French翻译任务上，我们得到一个新的最佳值。前一个任务中，我们最好的那个模型甚至优于所有先前提过的集成模型。

我们对于attention-based models的未来感到兴奋异常，而且计划将之应用于其它任务上。我们计划将Transformer扩展至涉及文字以外的输入、输出模式的问题，然后研究局部、受限的注意力机制来有效处理大型的输入与输出，如影像、音频与视频。

用来训练跟评估模型的程式码在 [https://github.com/tensorflow/tensor2tensor](https://github.com/tensorflow/tensor2tensor).

谢天谢地
