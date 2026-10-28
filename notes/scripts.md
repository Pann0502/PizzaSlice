java -jar .\theta\subprojects\xcfa\xcfa-cli\build\libs\theta-xcfa-cli-8.2.5-all.jar 
     --input-type C 
     --input .\src\witness_examples\01.c 
     --witness .\src\witness_examples\01.witness.yml 
     --svcomp 
     --debug

.-----------------------------------------------------------------------------------------------------

java -jar .\theta\subprojects\xcfa\xcfa-cli\build\libs\theta-xcfa-cli-8.2.5-all.jar `
    --input-type C 
    --input .\src\witness_examples\01.c 
    --svcomp 
    --debug

    -------------------------------------------------------------------------

# Using the standard version
fm-weck expert cpachecker:4.2.2 --witnessValidation --witness 01.witness.yml --spec unreach-call.prp --64 01.c

fm-weck expert cpachecker:4.2.2-validation-violation --witnessValidation --witness 01.witness.yml --spec unreach-call.prp --64 01.c

fm-weck expert witch:svcomp26 --witness-check 01.witness.yml --prp unreach-call --64 01.c

-----------------------------------------------------------

python lint\witnesslinter.py --witness ".\src\witness_examples\01.witness.yml" ".\src\witness_examples\01.c"