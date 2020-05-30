# Process:
#
# create ldpc matrices (width, height)
# - create using both personal implementation and library implementation
#
# create corresponding generator matrices
#
# encode message with generator matrices
#
# transmit default message
#
# decode default message with prprp max 100000
#
# extract message
#
# arguments:
# parity-check-width, parity-check-height, 1s per col, error rate
#
# implied:
# library ldpc construction: evenboth
# generator construction method: dense
# corruption: binary symmetric

clear

echo "generating parity check matrix through default implementation..."
./LDPC-codes/make-ldpc ./PipelineRES/ParityCheckMatrices/PipelineDefaultLibraryGenerated ${2} ${1} 1 evenboth ${3}
echo ""

echo "generating parity check matrix through python..."
# ./MakePCHKT ./PipelineRES/ParityCheckMatrices/PipelineDefaultPythonGenerated ${1} ${2}
python3 ./LDPC-TannerGraphs/Main.py ./PipelineRES/ParityCheckMatrices/PipelineDefaultPythonGenerated ${1} ${2}
echo ""

echo "creating generator matrix from library generated parity check matrix..."
./LDPC-codes/make-gen ./PipelineRES/ParityCheckMatrices/PipelineDefaultLibraryGenerated ./PipelineRES/GeneratorMatrices/PipelineDefaultLibraryGenerated dense
echo ""

echo "creating generator matrix from python generated parity check matrix..."
./LDPC-codes/make-gen ./PipelineRES/ParityCheckMatrices/PipelineDefaultPythonGenerated ./PipelineRES/GeneratorMatrices/PipelineDefaultPythonGenerated dense
echo ""

echo "encoding message with library generated generator matrix..."
./LDPC-codes/encode ./PipelineRES/ParityCheckMatrices/PipelineDefaultLibraryGenerated ./PipelineRES/GeneratorMatrices/PipelineDefaultLibraryGenerated ./PipelineRES/Message/PipelineDefault ./PipelineRES/Codewords/PipelineDefaultLibraryGenerated
echo ""

echo "encoding message with python generated generator matrix..."
./LDPC-codes/encode ./PipelineRES/ParityCheckMatrices/PipelineDefaultPythonGenerated ./PipelineRES/GeneratorMatrices/PipelineDefaultPythonGenerated ./PipelineRES/Message/PipelineDefault ./PipelineRES/Codewords/PipelineDefaultPythonGenerated
echo ""

echo "transmitting library encoded message with error probability ${4}..."
./LDPC-codes/transmit ./PipelineRES/Codewords/PipelineDefaultLibraryGenerated ./PipelineRES/ReceivedTransmissions/PipelineDefaultLibraryGenerated 1 bsc ${4}
echo ""

echo "transmitting python encoded messages with error probability ${4}..."
./LDPC-codes/transmit ./PipelineRES/Codewords/PipelineDefaultPythonGenerated ./PipelineRES/ReceivedTransmissions/PipelineDefaultPythonGenerated 1 bsc ${4}
echo ""

echo "decoding transmission for library generated parity matrix..."
./LDPC-codes/decode ./PipelineRES/ParityCheckMatrices/PipelineDefaultLibraryGenerated ./PipelineRES/ReceivedTransmissions/PipelineDefaultLibraryGenerated ./PipelineRES/DecodedTransmissions/PipelineDefaultLibraryGenerated bsc ${4} prprp 100
echo ""

echo "decoding transmission for python generated parity matrix..."
./LDPC-codes/decode ./PipelineRES/ParityCheckMatrices/PipelineDefaultPythonGenerated ./PipelineRES/ReceivedTransmissions/PipelineDefaultPythonGenerated ./PipelineRES/DecodedTransmissions/PipelineDefaultPythonGenerated bsc ${4} prprp 100
echo ""

echo "extracting both messages from decoded codewords..."
./LDPC-codes/extract ./PipelineRES/GeneratorMatrices/PipelineDefaultLibraryGenerated ./PipelineRES/DecodedTransmissions/PipelineDefaultLibraryGenerated ./PipelineRES/ExtractedMessages/PipelineDefaultLibraryGenerated
./LDPC-codes/extract ./PipelineRES/GeneratorMatrices/PipelineDefaultPythonGenerated ./PipelineRES/DecodedTransmissions/PipelineDefaultPythonGenerated ./PipelineRES/ExtractedMessages/PipelineDefaultPythonGenerated
echo "done"
echo ""