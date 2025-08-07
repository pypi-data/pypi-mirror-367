#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* matrix.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetrandom_ MATSETRANDOM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetrandom_ matsetrandom
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfactorgeterrorzeropivot_ MATFACTORGETERRORZEROPIVOT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfactorgeterrorzeropivot_ matfactorgeterrorzeropivot
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfactorgeterror_ MATFACTORGETERROR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfactorgeterror_ matfactorgeterror
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfactorclearerror_ MATFACTORCLEARERROR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfactorclearerror_ matfactorclearerror
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfindnonzerorows_ MATFINDNONZEROROWS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfindnonzerorows_ matfindnonzerorows
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfindzerorows_ MATFINDZEROROWS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfindzerorows_ matfindzerorows
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetdiagonalblock_ MATGETDIAGONALBLOCK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetdiagonalblock_ matgetdiagonalblock
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgettrace_ MATGETTRACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgettrace_ matgettrace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matrealpart_ MATREALPART
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matrealpart_ matrealpart
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matimaginarypart_ MATIMAGINARYPART
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matimaginarypart_ matimaginarypart
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmissingdiagonal_ MATMISSINGDIAGONAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmissingdiagonal_ matmissingdiagonal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matconjugate_ MATCONJUGATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matconjugate_ matconjugate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetrowuppertriangular_ MATGETROWUPPERTRIANGULAR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetrowuppertriangular_ matgetrowuppertriangular
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matrestorerowuppertriangular_ MATRESTOREROWUPPERTRIANGULAR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matrestorerowuppertriangular_ matrestorerowuppertriangular
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetoptionsprefix_ MATSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetoptionsprefix_ matsetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetoptionsprefixfactor_ MATSETOPTIONSPREFIXFACTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetoptionsprefixfactor_ matsetoptionsprefixfactor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matappendoptionsprefixfactor_ MATAPPENDOPTIONSPREFIXFACTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matappendoptionsprefixfactor_ matappendoptionsprefixfactor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matappendoptionsprefix_ MATAPPENDOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matappendoptionsprefix_ matappendoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetoptionsprefix_ MATGETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetoptionsprefix_ matgetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetstate_ MATGETSTATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetstate_ matgetstate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matresetpreallocation_ MATRESETPREALLOCATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matresetpreallocation_ matresetpreallocation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetup_ MATSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetup_ matsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matviewfromoptions_ MATVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matviewfromoptions_ matviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matview_ MATVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matview_ matview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matload_ MATLOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matload_ matload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matdestroy_ MATDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdestroy_ matdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetvalues_ MATSETVALUES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetvalues_ matsetvalues
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetvaluesis_ MATSETVALUESIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetvaluesis_ matsetvaluesis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetvaluesrowlocal_ MATSETVALUESROWLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetvaluesrowlocal_ matsetvaluesrowlocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetvaluesrow_ MATSETVALUESROW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetvaluesrow_ matsetvaluesrow
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetvaluesstencil_ MATSETVALUESSTENCIL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetvaluesstencil_ matsetvaluesstencil
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetvaluesblockedstencil_ MATSETVALUESBLOCKEDSTENCIL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetvaluesblockedstencil_ matsetvaluesblockedstencil
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetstencil_ MATSETSTENCIL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetstencil_ matsetstencil
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetvaluesblocked_ MATSETVALUESBLOCKED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetvaluesblocked_ matsetvaluesblocked
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetvalues_ MATGETVALUES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetvalues_ matgetvalues
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetvalueslocal_ MATGETVALUESLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetvalueslocal_ matgetvalueslocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetvaluesbatch_ MATSETVALUESBATCH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetvaluesbatch_ matsetvaluesbatch
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetlocaltoglobalmapping_ MATSETLOCALTOGLOBALMAPPING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetlocaltoglobalmapping_ matsetlocaltoglobalmapping
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetlocaltoglobalmapping_ MATGETLOCALTOGLOBALMAPPING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetlocaltoglobalmapping_ matgetlocaltoglobalmapping
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetlayouts_ MATSETLAYOUTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetlayouts_ matsetlayouts
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetlayouts_ MATGETLAYOUTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetlayouts_ matgetlayouts
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetvalueslocal_ MATSETVALUESLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetvalueslocal_ matsetvalueslocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetvaluesblockedlocal_ MATSETVALUESBLOCKEDLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetvaluesblockedlocal_ matsetvaluesblockedlocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmultdiagonalblock_ MATMULTDIAGONALBLOCK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmultdiagonalblock_ matmultdiagonalblock
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmult_ MATMULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmult_ matmult
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmulttranspose_ MATMULTTRANSPOSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmulttranspose_ matmulttranspose
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmulthermitiantranspose_ MATMULTHERMITIANTRANSPOSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmulthermitiantranspose_ matmulthermitiantranspose
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmultadd_ MATMULTADD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmultadd_ matmultadd
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmulttransposeadd_ MATMULTTRANSPOSEADD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmulttransposeadd_ matmulttransposeadd
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmulthermitiantransposeadd_ MATMULTHERMITIANTRANSPOSEADD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmulthermitiantransposeadd_ matmulthermitiantransposeadd
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetfactortype_ MATGETFACTORTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetfactortype_ matgetfactortype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetfactortype_ MATSETFACTORTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetfactortype_ matsetfactortype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetinfo_ MATGETINFO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetinfo_ matgetinfo
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matlufactor_ MATLUFACTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matlufactor_ matlufactor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matilufactor_ MATILUFACTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matilufactor_ matilufactor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matlufactorsymbolic_ MATLUFACTORSYMBOLIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matlufactorsymbolic_ matlufactorsymbolic
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matlufactornumeric_ MATLUFACTORNUMERIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matlufactornumeric_ matlufactornumeric
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcholeskyfactor_ MATCHOLESKYFACTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcholeskyfactor_ matcholeskyfactor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcholeskyfactorsymbolic_ MATCHOLESKYFACTORSYMBOLIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcholeskyfactorsymbolic_ matcholeskyfactorsymbolic
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcholeskyfactornumeric_ MATCHOLESKYFACTORNUMERIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcholeskyfactornumeric_ matcholeskyfactornumeric
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matqrfactor_ MATQRFACTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matqrfactor_ matqrfactor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matqrfactorsymbolic_ MATQRFACTORSYMBOLIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matqrfactorsymbolic_ matqrfactorsymbolic
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matqrfactornumeric_ MATQRFACTORNUMERIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matqrfactornumeric_ matqrfactornumeric
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsolve_ MATSOLVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsolve_ matsolve
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmatsolve_ MATMATSOLVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmatsolve_ matmatsolve
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmatsolvetranspose_ MATMATSOLVETRANSPOSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmatsolvetranspose_ matmatsolvetranspose
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmattransposesolve_ MATMATTRANSPOSESOLVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmattransposesolve_ matmattransposesolve
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matforwardsolve_ MATFORWARDSOLVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matforwardsolve_ matforwardsolve
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matbackwardsolve_ MATBACKWARDSOLVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matbackwardsolve_ matbackwardsolve
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsolveadd_ MATSOLVEADD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsolveadd_ matsolveadd
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsolvetranspose_ MATSOLVETRANSPOSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsolvetranspose_ matsolvetranspose
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsolvetransposeadd_ MATSOLVETRANSPOSEADD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsolvetransposeadd_ matsolvetransposeadd
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsor_ MATSOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsor_ matsor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcopy_ MATCOPY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcopy_ matcopy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matconvert_ MATCONVERT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matconvert_ matconvert
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfactorgetsolvertype_ MATFACTORGETSOLVERTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfactorgetsolvertype_ matfactorgetsolvertype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfactorgetcanuseordering_ MATFACTORGETCANUSEORDERING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfactorgetcanuseordering_ matfactorgetcanuseordering
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfactorgetpreferredordering_ MATFACTORGETPREFERREDORDERING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfactorgetpreferredordering_ matfactorgetpreferredordering
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetfactor_ MATGETFACTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetfactor_ matgetfactor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetfactoravailable_ MATGETFACTORAVAILABLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetfactoravailable_ matgetfactoravailable
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matduplicate_ MATDUPLICATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matduplicate_ matduplicate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetdiagonal_ MATGETDIAGONAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetdiagonal_ matgetdiagonal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetrowmin_ MATGETROWMIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetrowmin_ matgetrowmin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetrowminabs_ MATGETROWMINABS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetrowminabs_ matgetrowminabs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetrowmax_ MATGETROWMAX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetrowmax_ matgetrowmax
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetrowmaxabs_ MATGETROWMAXABS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetrowmaxabs_ matgetrowmaxabs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetrowsumabs_ MATGETROWSUMABS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetrowsumabs_ matgetrowsumabs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetrowsum_ MATGETROWSUM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetrowsum_ matgetrowsum
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mattransposesetprecursor_ MATTRANSPOSESETPRECURSOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mattransposesetprecursor_ mattransposesetprecursor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mattranspose_ MATTRANSPOSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mattranspose_ mattranspose
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mattransposesymbolic_ MATTRANSPOSESYMBOLIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mattransposesymbolic_ mattransposesymbolic
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matistranspose_ MATISTRANSPOSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matistranspose_ matistranspose
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mathermitiantranspose_ MATHERMITIANTRANSPOSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mathermitiantranspose_ mathermitiantranspose
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matishermitiantranspose_ MATISHERMITIANTRANSPOSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matishermitiantranspose_ matishermitiantranspose
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpermute_ MATPERMUTE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpermute_ matpermute
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matequal_ MATEQUAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matequal_ matequal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matdiagonalscale_ MATDIAGONALSCALE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdiagonalscale_ matdiagonalscale
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matscale_ MATSCALE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matscale_ matscale
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matnorm_ MATNORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matnorm_ matnorm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matassemblybegin_ MATASSEMBLYBEGIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matassemblybegin_ matassemblybegin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matassembled_ MATASSEMBLED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matassembled_ matassembled
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matassemblyend_ MATASSEMBLYEND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matassemblyend_ matassemblyend
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetoption_ MATSETOPTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetoption_ matsetoption
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetoption_ MATGETOPTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetoption_ matgetoption
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matzeroentries_ MATZEROENTRIES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matzeroentries_ matzeroentries
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matzerorowscolumns_ MATZEROROWSCOLUMNS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matzerorowscolumns_ matzerorowscolumns
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matzerorowscolumnsis_ MATZEROROWSCOLUMNSIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matzerorowscolumnsis_ matzerorowscolumnsis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matzerorows_ MATZEROROWS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matzerorows_ matzerorows
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matzerorowsis_ MATZEROROWSIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matzerorowsis_ matzerorowsis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matzerorowsstencil_ MATZEROROWSSTENCIL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matzerorowsstencil_ matzerorowsstencil
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matzerorowscolumnsstencil_ MATZEROROWSCOLUMNSSTENCIL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matzerorowscolumnsstencil_ matzerorowscolumnsstencil
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matzerorowslocal_ MATZEROROWSLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matzerorowslocal_ matzerorowslocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matzerorowslocalis_ MATZEROROWSLOCALIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matzerorowslocalis_ matzerorowslocalis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matzerorowscolumnslocal_ MATZEROROWSCOLUMNSLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matzerorowscolumnslocal_ matzerorowscolumnslocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matzerorowscolumnslocalis_ MATZEROROWSCOLUMNSLOCALIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matzerorowscolumnslocalis_ matzerorowscolumnslocalis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetsize_ MATGETSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetsize_ matgetsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetlocalsize_ MATGETLOCALSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetlocalsize_ matgetlocalsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetownershiprangecolumn_ MATGETOWNERSHIPRANGECOLUMN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetownershiprangecolumn_ matgetownershiprangecolumn
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetownershiprange_ MATGETOWNERSHIPRANGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetownershiprange_ matgetownershiprange
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetownershipis_ MATGETOWNERSHIPIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetownershipis_ matgetownershipis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matilufactorsymbolic_ MATILUFACTORSYMBOLIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matilufactorsymbolic_ matilufactorsymbolic
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define maticcfactorsymbolic_ MATICCFACTORSYMBOLIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define maticcfactorsymbolic_ maticcfactorsymbolic
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetseqnonzerostructure_ MATGETSEQNONZEROSTRUCTURE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetseqnonzerostructure_ matgetseqnonzerostructure
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matincreaseoverlap_ MATINCREASEOVERLAP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matincreaseoverlap_ matincreaseoverlap
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matincreaseoverlapsplit_ MATINCREASEOVERLAPSPLIT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matincreaseoverlapsplit_ matincreaseoverlapsplit
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetblocksize_ MATGETBLOCKSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetblocksize_ matgetblocksize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetblocksizes_ MATGETBLOCKSIZES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetblocksizes_ matgetblocksizes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetblocksize_ MATSETBLOCKSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetblocksize_ matsetblocksize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcomputevariableblockenvelope_ MATCOMPUTEVARIABLEBLOCKENVELOPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcomputevariableblockenvelope_ matcomputevariableblockenvelope
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matinvertvariableblockenvelope_ MATINVERTVARIABLEBLOCKENVELOPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matinvertvariableblockenvelope_ matinvertvariableblockenvelope
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetvariableblocksizes_ MATSETVARIABLEBLOCKSIZES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetvariableblocksizes_ matsetvariableblocksizes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetblocksizes_ MATSETBLOCKSIZES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetblocksizes_ matsetblocksizes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetblocksizesfrommats_ MATSETBLOCKSIZESFROMMATS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetblocksizesfrommats_ matsetblocksizesfrommats
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matresidual_ MATRESIDUAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matresidual_ matresidual
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcoloringpatch_ MATCOLORINGPATCH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcoloringpatch_ matcoloringpatch
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetunfactored_ MATSETUNFACTORED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetunfactored_ matsetunfactored
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatesubmatrix_ MATCREATESUBMATRIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatesubmatrix_ matcreatesubmatrix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpropagatesymmetryoptions_ MATPROPAGATESYMMETRYOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpropagatesymmetryoptions_ matpropagatesymmetryoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstashsetinitialsize_ MATSTASHSETINITIALSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstashsetinitialsize_ matstashsetinitialsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matinterpolateadd_ MATINTERPOLATEADD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matinterpolateadd_ matinterpolateadd
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matinterpolate_ MATINTERPOLATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matinterpolate_ matinterpolate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matrestrict_ MATRESTRICT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matrestrict_ matrestrict
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmatinterpolateadd_ MATMATINTERPOLATEADD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmatinterpolateadd_ matmatinterpolateadd
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmatinterpolate_ MATMATINTERPOLATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmatinterpolate_ matmatinterpolate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmatrestrict_ MATMATRESTRICT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmatrestrict_ matmatrestrict
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetnullspace_ MATGETNULLSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetnullspace_ matgetnullspace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetnullspace_ MATSETNULLSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetnullspace_ matsetnullspace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgettransposenullspace_ MATGETTRANSPOSENULLSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgettransposenullspace_ matgettransposenullspace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsettransposenullspace_ MATSETTRANSPOSENULLSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsettransposenullspace_ matsettransposenullspace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetnearnullspace_ MATSETNEARNULLSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetnearnullspace_ matsetnearnullspace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetnearnullspace_ MATGETNEARNULLSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetnearnullspace_ matgetnearnullspace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define maticcfactor_ MATICCFACTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define maticcfactor_ maticcfactor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matdiagonalscalelocal_ MATDIAGONALSCALELOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdiagonalscalelocal_ matdiagonalscalelocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetinertia_ MATGETINERTIA
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetinertia_ matgetinertia
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matissymmetric_ MATISSYMMETRIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matissymmetric_ matissymmetric
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matishermitian_ MATISHERMITIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matishermitian_ matishermitian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matissymmetricknown_ MATISSYMMETRICKNOWN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matissymmetricknown_ matissymmetricknown
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matisspdknown_ MATISSPDKNOWN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matisspdknown_ matisspdknown
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matishermitianknown_ MATISHERMITIANKNOWN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matishermitianknown_ matishermitianknown
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matisstructurallysymmetric_ MATISSTRUCTURALLYSYMMETRIC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matisstructurallysymmetric_ matisstructurallysymmetric
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matisstructurallysymmetricknown_ MATISSTRUCTURALLYSYMMETRICKNOWN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matisstructurallysymmetricknown_ matisstructurallysymmetricknown
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstashgetinfo_ MATSTASHGETINFO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstashgetinfo_ matstashgetinfo
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatevecs_ MATCREATEVECS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatevecs_ matcreatevecs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfactorinfoinitialize_ MATFACTORINFOINITIALIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfactorinfoinitialize_ matfactorinfoinitialize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfactorsetschuris_ MATFACTORSETSCHURIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfactorsetschuris_ matfactorsetschuris
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfactorcreateschurcomplement_ MATFACTORCREATESCHURCOMPLEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfactorcreateschurcomplement_ matfactorcreateschurcomplement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfactorgetschurcomplement_ MATFACTORGETSCHURCOMPLEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfactorgetschurcomplement_ matfactorgetschurcomplement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfactorrestoreschurcomplement_ MATFACTORRESTORESCHURCOMPLEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfactorrestoreschurcomplement_ matfactorrestoreschurcomplement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfactorsolveschurcomplementtranspose_ MATFACTORSOLVESCHURCOMPLEMENTTRANSPOSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfactorsolveschurcomplementtranspose_ matfactorsolveschurcomplementtranspose
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfactorsolveschurcomplement_ MATFACTORSOLVESCHURCOMPLEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfactorsolveschurcomplement_ matfactorsolveschurcomplement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfactorinvertschurcomplement_ MATFACTORINVERTSCHURCOMPLEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfactorinvertschurcomplement_ matfactorinvertschurcomplement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfactorfactorizeschurcomplement_ MATFACTORFACTORIZESCHURCOMPLEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfactorfactorizeschurcomplement_ matfactorfactorizeschurcomplement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matptap_ MATPTAP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matptap_ matptap
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matrart_ MATRART
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matrart_ matrart
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmatmult_ MATMATMULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmatmult_ matmatmult
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmattransposemult_ MATMATTRANSPOSEMULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmattransposemult_ matmattransposemult
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mattransposematmult_ MATTRANSPOSEMATMULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mattransposematmult_ mattransposematmult
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmatmatmult_ MATMATMATMULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmatmatmult_ matmatmatmult
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreateredundantmatrix_ MATCREATEREDUNDANTMATRIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreateredundantmatrix_ matcreateredundantmatrix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetlocalsubmatrix_ MATGETLOCALSUBMATRIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetlocalsubmatrix_ matgetlocalsubmatrix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matrestorelocalsubmatrix_ MATRESTORELOCALSUBMATRIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matrestorelocalsubmatrix_ matrestorelocalsubmatrix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfindzerodiagonals_ MATFINDZERODIAGONALS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfindzerodiagonals_ matfindzerodiagonals
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfindoffblockdiagonalentries_ MATFINDOFFBLOCKDIAGONALENTRIES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfindoffblockdiagonalentries_ matfindoffblockdiagonalentries
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matinvertvariableblockdiagonal_ MATINVERTVARIABLEBLOCKDIAGONAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matinvertvariableblockdiagonal_ matinvertvariableblockdiagonal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matinvertblockdiagonalmat_ MATINVERTBLOCKDIAGONALMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matinvertblockdiagonalmat_ matinvertblockdiagonalmat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mattransposecoloringdestroy_ MATTRANSPOSECOLORINGDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mattransposecoloringdestroy_ mattransposecoloringdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mattranscoloringapplysptoden_ MATTRANSCOLORINGAPPLYSPTODEN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mattranscoloringapplysptoden_ mattranscoloringapplysptoden
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mattranscoloringapplydentosp_ MATTRANSCOLORINGAPPLYDENTOSP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mattranscoloringapplydentosp_ mattranscoloringapplydentosp
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mattransposecoloringcreate_ MATTRANSPOSECOLORINGCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mattransposecoloringcreate_ mattransposecoloringcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetnonzerostate_ MATGETNONZEROSTATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetnonzerostate_ matgetnonzerostate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatempimatconcatenateseqmat_ MATCREATEMPIMATCONCATENATESEQMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatempimatconcatenateseqmat_ matcreatempimatconcatenateseqmat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsubdomainscreatecoalesce_ MATSUBDOMAINSCREATECOALESCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsubdomainscreatecoalesce_ matsubdomainscreatecoalesce
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgalerkin_ MATGALERKIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgalerkin_ matgalerkin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mathasoperation_ MATHASOPERATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mathasoperation_ mathasoperation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mathascongruentlayouts_ MATHASCONGRUENTLAYOUTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mathascongruentlayouts_ mathascongruentlayouts
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreategraph_ MATCREATEGRAPH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreategraph_ matcreategraph
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mateliminatezeros_ MATELIMINATEZEROS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mateliminatezeros_ mateliminatezeros
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matsetrandom_(Mat x,PetscRandom rctx, int *ierr)
{
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(rctx);
*ierr = MatSetRandom(
	(Mat)PetscToPointer((x) ),
	(PetscRandom)PetscToPointer((rctx) ));
}
PETSC_EXTERN void  matfactorgeterrorzeropivot_(Mat mat,PetscReal *pivot,PetscInt *row, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLREAL(pivot);
CHKFORTRANNULLINTEGER(row);
*ierr = MatFactorGetErrorZeroPivot(
	(Mat)PetscToPointer((mat) ),pivot,row);
}
PETSC_EXTERN void  matfactorgeterror_(Mat mat,MatFactorError *err, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatFactorGetError(
	(Mat)PetscToPointer((mat) ),err);
}
PETSC_EXTERN void  matfactorclearerror_(Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatFactorClearError(
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  matfindnonzerorows_(Mat mat,IS *keptrows, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool keptrows_null = !*(void**) keptrows ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(keptrows);
*ierr = MatFindNonzeroRows(
	(Mat)PetscToPointer((mat) ),keptrows);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! keptrows_null && !*(void**) keptrows) * (void **) keptrows = (void *)-2;
}
PETSC_EXTERN void  matfindzerorows_(Mat mat,IS *zerorows, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool zerorows_null = !*(void**) zerorows ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(zerorows);
*ierr = MatFindZeroRows(
	(Mat)PetscToPointer((mat) ),zerorows);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! zerorows_null && !*(void**) zerorows) * (void **) zerorows = (void *)-2;
}
PETSC_EXTERN void  matgetdiagonalblock_(Mat A,Mat *a, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool a_null = !*(void**) a ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(a);
*ierr = MatGetDiagonalBlock(
	(Mat)PetscToPointer((A) ),a);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! a_null && !*(void**) a) * (void **) a = (void *)-2;
}
PETSC_EXTERN void  matgettrace_(Mat mat,PetscScalar *trace, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLSCALAR(trace);
*ierr = MatGetTrace(
	(Mat)PetscToPointer((mat) ),trace);
}
PETSC_EXTERN void  matrealpart_(Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatRealPart(
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  matimaginarypart_(Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatImaginaryPart(
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  matmissingdiagonal_(Mat mat,PetscBool *missing,PetscInt *dd, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(dd);
*ierr = MatMissingDiagonal(
	(Mat)PetscToPointer((mat) ),missing,dd);
}
PETSC_EXTERN void  matconjugate_(Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatConjugate(
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  matgetrowuppertriangular_(Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatGetRowUpperTriangular(
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  matrestorerowuppertriangular_(Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatRestoreRowUpperTriangular(
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  matsetoptionsprefix_(Mat A, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = MatSetOptionsPrefix(
	(Mat)PetscToPointer((A) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  matsetoptionsprefixfactor_(Mat A, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = MatSetOptionsPrefixFactor(
	(Mat)PetscToPointer((A) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  matappendoptionsprefixfactor_(Mat A, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = MatAppendOptionsPrefixFactor(
	(Mat)PetscToPointer((A) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  matappendoptionsprefix_(Mat A, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = MatAppendOptionsPrefix(
	(Mat)PetscToPointer((A) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  matgetoptionsprefix_(Mat A, char *prefix, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
*ierr = MatGetOptionsPrefix(
	(Mat)PetscToPointer((A) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for prefix */
*ierr = PetscStrncpy(prefix, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, prefix, cl0);
}
PETSC_EXTERN void  matgetstate_(Mat A,PetscObjectState *state, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatGetState(
	(Mat)PetscToPointer((A) ),
	(PetscObjectState* )PetscToPointer((state) ));
}
PETSC_EXTERN void  matresetpreallocation_(Mat A, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatResetPreallocation(
	(Mat)PetscToPointer((A) ));
}
PETSC_EXTERN void  matsetup_(Mat A, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatSetUp(
	(Mat)PetscToPointer((A) ));
}
PETSC_EXTERN void  matviewfromoptions_(Mat A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = MatViewFromOptions(
	(Mat)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  matview_(Mat mat,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(viewer);
*ierr = MatView(
	(Mat)PetscToPointer((mat) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  matload_(Mat mat,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(viewer);
*ierr = MatLoad(
	(Mat)PetscToPointer((mat) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  matdestroy_(Mat *A, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(A);
 PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
*ierr = MatDestroy(A);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(A);
 }
PETSC_EXTERN void  matsetvalues_(Mat mat,PetscInt *m, PetscInt idxm[],PetscInt *n, PetscInt idxn[], PetscScalar v[],InsertMode *addv, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(idxm);
CHKFORTRANNULLINTEGER(idxn);
CHKFORTRANNULLSCALAR(v);
*ierr = MatSetValues(
	(Mat)PetscToPointer((mat) ),*m,idxm,*n,idxn,v,*addv);
}
PETSC_EXTERN void  matsetvaluesis_(Mat mat,IS ism,IS isn, PetscScalar v[],InsertMode *addv, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(ism);
CHKFORTRANNULLOBJECT(isn);
CHKFORTRANNULLSCALAR(v);
*ierr = MatSetValuesIS(
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((ism) ),
	(IS)PetscToPointer((isn) ),v,*addv);
}
PETSC_EXTERN void  matsetvaluesrowlocal_(Mat mat,PetscInt *row, PetscScalar v[], int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLSCALAR(v);
*ierr = MatSetValuesRowLocal(
	(Mat)PetscToPointer((mat) ),*row,v);
}
PETSC_EXTERN void  matsetvaluesrow_(Mat mat,PetscInt *row, PetscScalar v[], int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLSCALAR(v);
*ierr = MatSetValuesRow(
	(Mat)PetscToPointer((mat) ),*row,v);
}
PETSC_EXTERN void  matsetvaluesstencil_(Mat mat,PetscInt *m, MatStencil idxm[],PetscInt *n, MatStencil idxn[], PetscScalar v[],InsertMode *addv, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLSCALAR(v);
*ierr = MatSetValuesStencil(
	(Mat)PetscToPointer((mat) ),*m,idxm,*n,idxn,v,*addv);
}
PETSC_EXTERN void  matsetvaluesblockedstencil_(Mat mat,PetscInt *m, MatStencil idxm[],PetscInt *n, MatStencil idxn[], PetscScalar v[],InsertMode *addv, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLSCALAR(v);
*ierr = MatSetValuesBlockedStencil(
	(Mat)PetscToPointer((mat) ),*m,idxm,*n,idxn,v,*addv);
}
PETSC_EXTERN void  matsetstencil_(Mat mat,PetscInt *dim, PetscInt dims[], PetscInt starts[],PetscInt *dof, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(dims);
CHKFORTRANNULLINTEGER(starts);
*ierr = MatSetStencil(
	(Mat)PetscToPointer((mat) ),*dim,dims,starts,*dof);
}
PETSC_EXTERN void  matsetvaluesblocked_(Mat mat,PetscInt *m, PetscInt idxm[],PetscInt *n, PetscInt idxn[], PetscScalar v[],InsertMode *addv, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(idxm);
CHKFORTRANNULLINTEGER(idxn);
CHKFORTRANNULLSCALAR(v);
*ierr = MatSetValuesBlocked(
	(Mat)PetscToPointer((mat) ),*m,idxm,*n,idxn,v,*addv);
}
PETSC_EXTERN void  matgetvalues_(Mat mat,PetscInt *m, PetscInt idxm[],PetscInt *n, PetscInt idxn[],PetscScalar v[], int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(idxm);
CHKFORTRANNULLINTEGER(idxn);
CHKFORTRANNULLSCALAR(v);
*ierr = MatGetValues(
	(Mat)PetscToPointer((mat) ),*m,idxm,*n,idxn,v);
}
PETSC_EXTERN void  matgetvalueslocal_(Mat mat,PetscInt *nrow, PetscInt irow[],PetscInt *ncol, PetscInt icol[],PetscScalar y[], int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(irow);
CHKFORTRANNULLINTEGER(icol);
CHKFORTRANNULLSCALAR(y);
*ierr = MatGetValuesLocal(
	(Mat)PetscToPointer((mat) ),*nrow,irow,*ncol,icol,y);
}
PETSC_EXTERN void  matsetvaluesbatch_(Mat mat,PetscInt *nb,PetscInt *bs,PetscInt rows[], PetscScalar v[], int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(rows);
CHKFORTRANNULLSCALAR(v);
*ierr = MatSetValuesBatch(
	(Mat)PetscToPointer((mat) ),*nb,*bs,rows,v);
}
PETSC_EXTERN void  matsetlocaltoglobalmapping_(Mat x,ISLocalToGlobalMapping rmapping,ISLocalToGlobalMapping cmapping, int *ierr)
{
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(rmapping);
CHKFORTRANNULLOBJECT(cmapping);
*ierr = MatSetLocalToGlobalMapping(
	(Mat)PetscToPointer((x) ),
	(ISLocalToGlobalMapping)PetscToPointer((rmapping) ),
	(ISLocalToGlobalMapping)PetscToPointer((cmapping) ));
}
PETSC_EXTERN void  matgetlocaltoglobalmapping_(Mat A,ISLocalToGlobalMapping *rmapping,ISLocalToGlobalMapping *cmapping, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool rmapping_null = !*(void**) rmapping ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(rmapping);
PetscBool cmapping_null = !*(void**) cmapping ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(cmapping);
*ierr = MatGetLocalToGlobalMapping(
	(Mat)PetscToPointer((A) ),rmapping,cmapping);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! rmapping_null && !*(void**) rmapping) * (void **) rmapping = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! cmapping_null && !*(void**) cmapping) * (void **) cmapping = (void *)-2;
}
PETSC_EXTERN void  matsetlayouts_(Mat A,PetscLayout rmap,PetscLayout cmap, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(rmap);
CHKFORTRANNULLOBJECT(cmap);
*ierr = MatSetLayouts(
	(Mat)PetscToPointer((A) ),
	(PetscLayout)PetscToPointer((rmap) ),
	(PetscLayout)PetscToPointer((cmap) ));
}
PETSC_EXTERN void  matgetlayouts_(Mat A,PetscLayout *rmap,PetscLayout *cmap, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool rmap_null = !*(void**) rmap ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(rmap);
PetscBool cmap_null = !*(void**) cmap ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(cmap);
*ierr = MatGetLayouts(
	(Mat)PetscToPointer((A) ),rmap,cmap);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! rmap_null && !*(void**) rmap) * (void **) rmap = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! cmap_null && !*(void**) cmap) * (void **) cmap = (void *)-2;
}
PETSC_EXTERN void  matsetvalueslocal_(Mat mat,PetscInt *nrow, PetscInt irow[],PetscInt *ncol, PetscInt icol[], PetscScalar y[],InsertMode *addv, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(irow);
CHKFORTRANNULLINTEGER(icol);
CHKFORTRANNULLSCALAR(y);
*ierr = MatSetValuesLocal(
	(Mat)PetscToPointer((mat) ),*nrow,irow,*ncol,icol,y,*addv);
}
PETSC_EXTERN void  matsetvaluesblockedlocal_(Mat mat,PetscInt *nrow, PetscInt irow[],PetscInt *ncol, PetscInt icol[], PetscScalar y[],InsertMode *addv, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(irow);
CHKFORTRANNULLINTEGER(icol);
CHKFORTRANNULLSCALAR(y);
*ierr = MatSetValuesBlockedLocal(
	(Mat)PetscToPointer((mat) ),*nrow,irow,*ncol,icol,y,*addv);
}
PETSC_EXTERN void  matmultdiagonalblock_(Mat mat,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = MatMultDiagonalBlock(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  matmult_(Mat mat,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = MatMult(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  matmulttranspose_(Mat mat,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = MatMultTranspose(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  matmulthermitiantranspose_(Mat mat,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = MatMultHermitianTranspose(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  matmultadd_(Mat mat,Vec v1,Vec v2,Vec v3, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(v1);
CHKFORTRANNULLOBJECT(v2);
CHKFORTRANNULLOBJECT(v3);
*ierr = MatMultAdd(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((v1) ),
	(Vec)PetscToPointer((v2) ),
	(Vec)PetscToPointer((v3) ));
}
PETSC_EXTERN void  matmulttransposeadd_(Mat mat,Vec v1,Vec v2,Vec v3, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(v1);
CHKFORTRANNULLOBJECT(v2);
CHKFORTRANNULLOBJECT(v3);
*ierr = MatMultTransposeAdd(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((v1) ),
	(Vec)PetscToPointer((v2) ),
	(Vec)PetscToPointer((v3) ));
}
PETSC_EXTERN void  matmulthermitiantransposeadd_(Mat mat,Vec v1,Vec v2,Vec v3, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(v1);
CHKFORTRANNULLOBJECT(v2);
CHKFORTRANNULLOBJECT(v3);
*ierr = MatMultHermitianTransposeAdd(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((v1) ),
	(Vec)PetscToPointer((v2) ),
	(Vec)PetscToPointer((v3) ));
}
PETSC_EXTERN void  matgetfactortype_(Mat mat,MatFactorType *t, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatGetFactorType(
	(Mat)PetscToPointer((mat) ),t);
}
PETSC_EXTERN void  matsetfactortype_(Mat mat,MatFactorType *t, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatSetFactorType(
	(Mat)PetscToPointer((mat) ),*t);
}
PETSC_EXTERN void  matgetinfo_(Mat mat,MatInfoType *flag,MatInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatGetInfo(
	(Mat)PetscToPointer((mat) ),*flag,info);
}
PETSC_EXTERN void  matlufactor_(Mat mat,IS row,IS col, MatFactorInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(row);
CHKFORTRANNULLOBJECT(col);
*ierr = MatLUFactor(
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((row) ),
	(IS)PetscToPointer((col) ),info);
}
PETSC_EXTERN void  matilufactor_(Mat mat,IS row,IS col, MatFactorInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(row);
CHKFORTRANNULLOBJECT(col);
*ierr = MatILUFactor(
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((row) ),
	(IS)PetscToPointer((col) ),info);
}
PETSC_EXTERN void  matlufactorsymbolic_(Mat fact,Mat mat,IS row,IS col, MatFactorInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(fact);
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(row);
CHKFORTRANNULLOBJECT(col);
*ierr = MatLUFactorSymbolic(
	(Mat)PetscToPointer((fact) ),
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((row) ),
	(IS)PetscToPointer((col) ),info);
}
PETSC_EXTERN void  matlufactornumeric_(Mat fact,Mat mat, MatFactorInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(fact);
CHKFORTRANNULLOBJECT(mat);
*ierr = MatLUFactorNumeric(
	(Mat)PetscToPointer((fact) ),
	(Mat)PetscToPointer((mat) ),info);
}
PETSC_EXTERN void  matcholeskyfactor_(Mat mat,IS perm, MatFactorInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(perm);
*ierr = MatCholeskyFactor(
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((perm) ),info);
}
PETSC_EXTERN void  matcholeskyfactorsymbolic_(Mat fact,Mat mat,IS perm, MatFactorInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(fact);
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(perm);
*ierr = MatCholeskyFactorSymbolic(
	(Mat)PetscToPointer((fact) ),
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((perm) ),info);
}
PETSC_EXTERN void  matcholeskyfactornumeric_(Mat fact,Mat mat, MatFactorInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(fact);
CHKFORTRANNULLOBJECT(mat);
*ierr = MatCholeskyFactorNumeric(
	(Mat)PetscToPointer((fact) ),
	(Mat)PetscToPointer((mat) ),info);
}
PETSC_EXTERN void  matqrfactor_(Mat mat,IS col, MatFactorInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(col);
*ierr = MatQRFactor(
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((col) ),info);
}
PETSC_EXTERN void  matqrfactorsymbolic_(Mat fact,Mat mat,IS col, MatFactorInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(fact);
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(col);
*ierr = MatQRFactorSymbolic(
	(Mat)PetscToPointer((fact) ),
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((col) ),info);
}
PETSC_EXTERN void  matqrfactornumeric_(Mat fact,Mat mat, MatFactorInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(fact);
CHKFORTRANNULLOBJECT(mat);
*ierr = MatQRFactorNumeric(
	(Mat)PetscToPointer((fact) ),
	(Mat)PetscToPointer((mat) ),info);
}
PETSC_EXTERN void  matsolve_(Mat mat,Vec b,Vec x, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(b);
CHKFORTRANNULLOBJECT(x);
*ierr = MatSolve(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((b) ),
	(Vec)PetscToPointer((x) ));
}
PETSC_EXTERN void  matmatsolve_(Mat A,Mat B,Mat X, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLOBJECT(X);
*ierr = MatMatSolve(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ),
	(Mat)PetscToPointer((X) ));
}
PETSC_EXTERN void  matmatsolvetranspose_(Mat A,Mat B,Mat X, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLOBJECT(X);
*ierr = MatMatSolveTranspose(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ),
	(Mat)PetscToPointer((X) ));
}
PETSC_EXTERN void  matmattransposesolve_(Mat A,Mat Bt,Mat X, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(Bt);
CHKFORTRANNULLOBJECT(X);
*ierr = MatMatTransposeSolve(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((Bt) ),
	(Mat)PetscToPointer((X) ));
}
PETSC_EXTERN void  matforwardsolve_(Mat mat,Vec b,Vec x, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(b);
CHKFORTRANNULLOBJECT(x);
*ierr = MatForwardSolve(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((b) ),
	(Vec)PetscToPointer((x) ));
}
PETSC_EXTERN void  matbackwardsolve_(Mat mat,Vec b,Vec x, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(b);
CHKFORTRANNULLOBJECT(x);
*ierr = MatBackwardSolve(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((b) ),
	(Vec)PetscToPointer((x) ));
}
PETSC_EXTERN void  matsolveadd_(Mat mat,Vec b,Vec y,Vec x, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(b);
CHKFORTRANNULLOBJECT(y);
CHKFORTRANNULLOBJECT(x);
*ierr = MatSolveAdd(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((b) ),
	(Vec)PetscToPointer((y) ),
	(Vec)PetscToPointer((x) ));
}
PETSC_EXTERN void  matsolvetranspose_(Mat mat,Vec b,Vec x, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(b);
CHKFORTRANNULLOBJECT(x);
*ierr = MatSolveTranspose(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((b) ),
	(Vec)PetscToPointer((x) ));
}
PETSC_EXTERN void  matsolvetransposeadd_(Mat mat,Vec b,Vec y,Vec x, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(b);
CHKFORTRANNULLOBJECT(y);
CHKFORTRANNULLOBJECT(x);
*ierr = MatSolveTransposeAdd(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((b) ),
	(Vec)PetscToPointer((y) ),
	(Vec)PetscToPointer((x) ));
}
PETSC_EXTERN void  matsor_(Mat mat,Vec b,PetscReal *omega,MatSORType *flag,PetscReal *shift,PetscInt *its,PetscInt *lits,Vec x, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(b);
CHKFORTRANNULLOBJECT(x);
*ierr = MatSOR(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((b) ),*omega,*flag,*shift,*its,*lits,
	(Vec)PetscToPointer((x) ));
}
PETSC_EXTERN void  matcopy_(Mat A,Mat B,MatStructure *str, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
*ierr = MatCopy(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ),*str);
}
PETSC_EXTERN void  matconvert_(Mat mat,char *newtype,MatReuse *reuse,Mat *M, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
PetscBool M_null = !*(void**) M ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(M);
/* insert Fortran-to-C conversion for newtype */
  FIXCHAR(newtype,cl0,_cltmp0);
*ierr = MatConvert(
	(Mat)PetscToPointer((mat) ),_cltmp0,*reuse,M);
  FREECHAR(newtype,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! M_null && !*(void**) M) * (void **) M = (void *)-2;
}
PETSC_EXTERN void  matfactorgetsolvertype_(Mat mat,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
*ierr = MatFactorGetSolverType(
	(Mat)PetscToPointer((mat) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  matfactorgetcanuseordering_(Mat mat,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatFactorGetCanUseOrdering(
	(Mat)PetscToPointer((mat) ),flg);
}
PETSC_EXTERN void  matfactorgetpreferredordering_(Mat mat,MatFactorType *ftype,char *otype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
*ierr = MatFactorGetPreferredOrdering(
	(Mat)PetscToPointer((mat) ),*ftype,(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for otype */
*ierr = PetscStrncpy(otype, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, otype, cl0);
}
PETSC_EXTERN void  matgetfactor_(Mat mat,char *type,MatFactorType *ftype,Mat *f, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
PetscBool f_null = !*(void**) f ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(f);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = MatGetFactor(
	(Mat)PetscToPointer((mat) ),_cltmp0,*ftype,f);
  FREECHAR(type,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! f_null && !*(void**) f) * (void **) f = (void *)-2;
}
PETSC_EXTERN void  matgetfactoravailable_(Mat mat,char *type,MatFactorType *ftype,PetscBool *flg, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = MatGetFactorAvailable(
	(Mat)PetscToPointer((mat) ),_cltmp0,*ftype,flg);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  matduplicate_(Mat mat,MatDuplicateOption *op,Mat *M, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool M_null = !*(void**) M ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(M);
*ierr = MatDuplicate(
	(Mat)PetscToPointer((mat) ),*op,M);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! M_null && !*(void**) M) * (void **) M = (void *)-2;
}
PETSC_EXTERN void  matgetdiagonal_(Mat mat,Vec v, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(v);
*ierr = MatGetDiagonal(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((v) ));
}
PETSC_EXTERN void  matgetrowmin_(Mat mat,Vec v,PetscInt idx[], int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(v);
CHKFORTRANNULLINTEGER(idx);
*ierr = MatGetRowMin(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((v) ),idx);
}
PETSC_EXTERN void  matgetrowminabs_(Mat mat,Vec v,PetscInt idx[], int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(v);
CHKFORTRANNULLINTEGER(idx);
*ierr = MatGetRowMinAbs(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((v) ),idx);
}
PETSC_EXTERN void  matgetrowmax_(Mat mat,Vec v,PetscInt idx[], int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(v);
CHKFORTRANNULLINTEGER(idx);
*ierr = MatGetRowMax(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((v) ),idx);
}
PETSC_EXTERN void  matgetrowmaxabs_(Mat mat,Vec v,PetscInt idx[], int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(v);
CHKFORTRANNULLINTEGER(idx);
*ierr = MatGetRowMaxAbs(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((v) ),idx);
}
PETSC_EXTERN void  matgetrowsumabs_(Mat mat,Vec v, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(v);
*ierr = MatGetRowSumAbs(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((v) ));
}
PETSC_EXTERN void  matgetrowsum_(Mat mat,Vec v, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(v);
*ierr = MatGetRowSum(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((v) ));
}
PETSC_EXTERN void  mattransposesetprecursor_(Mat mat,Mat B, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(B);
*ierr = MatTransposeSetPrecursor(
	(Mat)PetscToPointer((mat) ),
	(Mat)PetscToPointer((B) ));
}
PETSC_EXTERN void  mattranspose_(Mat mat,MatReuse *reuse,Mat *B, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool B_null = !*(void**) B ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(B);
*ierr = MatTranspose(
	(Mat)PetscToPointer((mat) ),*reuse,B);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! B_null && !*(void**) B) * (void **) B = (void *)-2;
}
PETSC_EXTERN void  mattransposesymbolic_(Mat A,Mat *B, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool B_null = !*(void**) B ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(B);
*ierr = MatTransposeSymbolic(
	(Mat)PetscToPointer((A) ),B);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! B_null && !*(void**) B) * (void **) B = (void *)-2;
}
PETSC_EXTERN void  matistranspose_(Mat A,Mat B,PetscReal *tol,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
*ierr = MatIsTranspose(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ),*tol,flg);
}
PETSC_EXTERN void  mathermitiantranspose_(Mat mat,MatReuse *reuse,Mat *B, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool B_null = !*(void**) B ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(B);
*ierr = MatHermitianTranspose(
	(Mat)PetscToPointer((mat) ),*reuse,B);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! B_null && !*(void**) B) * (void **) B = (void *)-2;
}
PETSC_EXTERN void  matishermitiantranspose_(Mat A,Mat B,PetscReal *tol,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
*ierr = MatIsHermitianTranspose(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ),*tol,flg);
}
PETSC_EXTERN void  matpermute_(Mat mat,IS row,IS col,Mat *B, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(row);
CHKFORTRANNULLOBJECT(col);
PetscBool B_null = !*(void**) B ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(B);
*ierr = MatPermute(
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((row) ),
	(IS)PetscToPointer((col) ),B);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! B_null && !*(void**) B) * (void **) B = (void *)-2;
}
PETSC_EXTERN void  matequal_(Mat A,Mat B,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
*ierr = MatEqual(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ),flg);
}
PETSC_EXTERN void  matdiagonalscale_(Mat mat,Vec l,Vec r, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(l);
CHKFORTRANNULLOBJECT(r);
*ierr = MatDiagonalScale(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((l) ),
	(Vec)PetscToPointer((r) ));
}
PETSC_EXTERN void  matscale_(Mat mat,PetscScalar *a, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatScale(
	(Mat)PetscToPointer((mat) ),*a);
}
PETSC_EXTERN void  matnorm_(Mat mat,NormType *type,PetscReal *nrm, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLREAL(nrm);
*ierr = MatNorm(
	(Mat)PetscToPointer((mat) ),*type,nrm);
}
PETSC_EXTERN void  matassemblybegin_(Mat mat,MatAssemblyType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatAssemblyBegin(
	(Mat)PetscToPointer((mat) ),*type);
}
PETSC_EXTERN void  matassembled_(Mat mat,PetscBool *assembled, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatAssembled(
	(Mat)PetscToPointer((mat) ),assembled);
}
PETSC_EXTERN void  matassemblyend_(Mat mat,MatAssemblyType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatAssemblyEnd(
	(Mat)PetscToPointer((mat) ),*type);
}
PETSC_EXTERN void  matsetoption_(Mat mat,MatOption *op,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatSetOption(
	(Mat)PetscToPointer((mat) ),*op,*flg);
}
PETSC_EXTERN void  matgetoption_(Mat mat,MatOption *op,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatGetOption(
	(Mat)PetscToPointer((mat) ),*op,flg);
}
PETSC_EXTERN void  matzeroentries_(Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatZeroEntries(
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  matzerorowscolumns_(Mat mat,PetscInt *numRows, PetscInt rows[],PetscScalar *diag,Vec x,Vec b, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(rows);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(b);
*ierr = MatZeroRowsColumns(
	(Mat)PetscToPointer((mat) ),*numRows,rows,*diag,
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((b) ));
}
PETSC_EXTERN void  matzerorowscolumnsis_(Mat mat,IS is,PetscScalar *diag,Vec x,Vec b, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(b);
*ierr = MatZeroRowsColumnsIS(
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((is) ),*diag,
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((b) ));
}
PETSC_EXTERN void  matzerorows_(Mat mat,PetscInt *numRows, PetscInt rows[],PetscScalar *diag,Vec x,Vec b, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(rows);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(b);
*ierr = MatZeroRows(
	(Mat)PetscToPointer((mat) ),*numRows,rows,*diag,
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((b) ));
}
PETSC_EXTERN void  matzerorowsis_(Mat mat,IS is,PetscScalar *diag,Vec x,Vec b, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(b);
*ierr = MatZeroRowsIS(
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((is) ),*diag,
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((b) ));
}
PETSC_EXTERN void  matzerorowsstencil_(Mat mat,PetscInt *numRows, MatStencil rows[],PetscScalar *diag,Vec x,Vec b, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(b);
*ierr = MatZeroRowsStencil(
	(Mat)PetscToPointer((mat) ),*numRows,rows,*diag,
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((b) ));
}
PETSC_EXTERN void  matzerorowscolumnsstencil_(Mat mat,PetscInt *numRows, MatStencil rows[],PetscScalar *diag,Vec x,Vec b, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(b);
*ierr = MatZeroRowsColumnsStencil(
	(Mat)PetscToPointer((mat) ),*numRows,rows,*diag,
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((b) ));
}
PETSC_EXTERN void  matzerorowslocal_(Mat mat,PetscInt *numRows, PetscInt rows[],PetscScalar *diag,Vec x,Vec b, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(rows);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(b);
*ierr = MatZeroRowsLocal(
	(Mat)PetscToPointer((mat) ),*numRows,rows,*diag,
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((b) ));
}
PETSC_EXTERN void  matzerorowslocalis_(Mat mat,IS is,PetscScalar *diag,Vec x,Vec b, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(b);
*ierr = MatZeroRowsLocalIS(
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((is) ),*diag,
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((b) ));
}
PETSC_EXTERN void  matzerorowscolumnslocal_(Mat mat,PetscInt *numRows, PetscInt rows[],PetscScalar *diag,Vec x,Vec b, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(rows);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(b);
*ierr = MatZeroRowsColumnsLocal(
	(Mat)PetscToPointer((mat) ),*numRows,rows,*diag,
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((b) ));
}
PETSC_EXTERN void  matzerorowscolumnslocalis_(Mat mat,IS is,PetscScalar *diag,Vec x,Vec b, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(b);
*ierr = MatZeroRowsColumnsLocalIS(
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((is) ),*diag,
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((b) ));
}
PETSC_EXTERN void  matgetsize_(Mat mat,PetscInt *m,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(m);
CHKFORTRANNULLINTEGER(n);
*ierr = MatGetSize(
	(Mat)PetscToPointer((mat) ),m,n);
}
PETSC_EXTERN void  matgetlocalsize_(Mat mat,PetscInt *m,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(m);
CHKFORTRANNULLINTEGER(n);
*ierr = MatGetLocalSize(
	(Mat)PetscToPointer((mat) ),m,n);
}
PETSC_EXTERN void  matgetownershiprangecolumn_(Mat mat,PetscInt *m,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(m);
CHKFORTRANNULLINTEGER(n);
*ierr = MatGetOwnershipRangeColumn(
	(Mat)PetscToPointer((mat) ),m,n);
}
PETSC_EXTERN void  matgetownershiprange_(Mat mat,PetscInt *m,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(m);
CHKFORTRANNULLINTEGER(n);
*ierr = MatGetOwnershipRange(
	(Mat)PetscToPointer((mat) ),m,n);
}
PETSC_EXTERN void  matgetownershipis_(Mat A,IS *rows,IS *cols, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool rows_null = !*(void**) rows ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(rows);
PetscBool cols_null = !*(void**) cols ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(cols);
*ierr = MatGetOwnershipIS(
	(Mat)PetscToPointer((A) ),rows,cols);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! rows_null && !*(void**) rows) * (void **) rows = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! cols_null && !*(void**) cols) * (void **) cols = (void *)-2;
}
PETSC_EXTERN void  matilufactorsymbolic_(Mat fact,Mat mat,IS row,IS col, MatFactorInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(fact);
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(row);
CHKFORTRANNULLOBJECT(col);
*ierr = MatILUFactorSymbolic(
	(Mat)PetscToPointer((fact) ),
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((row) ),
	(IS)PetscToPointer((col) ),info);
}
PETSC_EXTERN void  maticcfactorsymbolic_(Mat fact,Mat mat,IS perm, MatFactorInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(fact);
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(perm);
*ierr = MatICCFactorSymbolic(
	(Mat)PetscToPointer((fact) ),
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((perm) ),info);
}
PETSC_EXTERN void  matgetseqnonzerostructure_(Mat mat,Mat *matstruct, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool matstruct_null = !*(void**) matstruct ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(matstruct);
*ierr = MatGetSeqNonzeroStructure(
	(Mat)PetscToPointer((mat) ),matstruct);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! matstruct_null && !*(void**) matstruct) * (void **) matstruct = (void *)-2;
}
PETSC_EXTERN void  matincreaseoverlap_(Mat mat,PetscInt *n,IS is[],PetscInt *ov, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
*ierr = MatIncreaseOverlap(
	(Mat)PetscToPointer((mat) ),*n,is,*ov);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
PETSC_EXTERN void  matincreaseoverlapsplit_(Mat mat,PetscInt *n,IS is[],PetscInt *ov, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
*ierr = MatIncreaseOverlapSplit(
	(Mat)PetscToPointer((mat) ),*n,is,*ov);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
PETSC_EXTERN void  matgetblocksize_(Mat mat,PetscInt *bs, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(bs);
*ierr = MatGetBlockSize(
	(Mat)PetscToPointer((mat) ),bs);
}
PETSC_EXTERN void  matgetblocksizes_(Mat mat,PetscInt *rbs,PetscInt *cbs, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(rbs);
CHKFORTRANNULLINTEGER(cbs);
*ierr = MatGetBlockSizes(
	(Mat)PetscToPointer((mat) ),rbs,cbs);
}
PETSC_EXTERN void  matsetblocksize_(Mat mat,PetscInt *bs, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatSetBlockSize(
	(Mat)PetscToPointer((mat) ),*bs);
}
PETSC_EXTERN void  matcomputevariableblockenvelope_(Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatComputeVariableBlockEnvelope(
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  matinvertvariableblockenvelope_(Mat A,MatReuse *reuse,Mat *C, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool C_null = !*(void**) C ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(C);
*ierr = MatInvertVariableBlockEnvelope(
	(Mat)PetscToPointer((A) ),*reuse,C);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! C_null && !*(void**) C) * (void **) C = (void *)-2;
}
PETSC_EXTERN void  matsetvariableblocksizes_(Mat mat,PetscInt *nblocks, PetscInt bsizes[], int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(bsizes);
*ierr = MatSetVariableBlockSizes(
	(Mat)PetscToPointer((mat) ),*nblocks,bsizes);
}
PETSC_EXTERN void  matsetblocksizes_(Mat mat,PetscInt *rbs,PetscInt *cbs, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatSetBlockSizes(
	(Mat)PetscToPointer((mat) ),*rbs,*cbs);
}
PETSC_EXTERN void  matsetblocksizesfrommats_(Mat mat,Mat fromRow,Mat fromCol, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(fromRow);
CHKFORTRANNULLOBJECT(fromCol);
*ierr = MatSetBlockSizesFromMats(
	(Mat)PetscToPointer((mat) ),
	(Mat)PetscToPointer((fromRow) ),
	(Mat)PetscToPointer((fromCol) ));
}
PETSC_EXTERN void  matresidual_(Mat mat,Vec b,Vec x,Vec r, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(b);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(r);
*ierr = MatResidual(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((b) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((r) ));
}
PETSC_EXTERN void  matcoloringpatch_(Mat mat,PetscInt *ncolors,PetscInt *n,ISColoringValue colorarray[],ISColoring *iscoloring, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool iscoloring_null = !*(void**) iscoloring ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(iscoloring);
*ierr = MatColoringPatch(
	(Mat)PetscToPointer((mat) ),*ncolors,*n,
	(ISColoringValue* )PetscToPointer((colorarray) ),iscoloring);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! iscoloring_null && !*(void**) iscoloring) * (void **) iscoloring = (void *)-2;
}
PETSC_EXTERN void  matsetunfactored_(Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatSetUnfactored(
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  matcreatesubmatrix_(Mat mat,IS isrow,IS iscol,MatReuse *cll,Mat *newmat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(isrow);
CHKFORTRANNULLOBJECT(iscol);
PetscBool newmat_null = !*(void**) newmat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newmat);
*ierr = MatCreateSubMatrix(
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((isrow) ),
	(IS)PetscToPointer((iscol) ),*cll,newmat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newmat_null && !*(void**) newmat) * (void **) newmat = (void *)-2;
}
PETSC_EXTERN void  matpropagatesymmetryoptions_(Mat A,Mat B, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
*ierr = MatPropagateSymmetryOptions(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ));
}
PETSC_EXTERN void  matstashsetinitialsize_(Mat mat,PetscInt *size,PetscInt *bsize, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatStashSetInitialSize(
	(Mat)PetscToPointer((mat) ),*size,*bsize);
}
PETSC_EXTERN void  matinterpolateadd_(Mat A,Vec x,Vec y,Vec w, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
CHKFORTRANNULLOBJECT(w);
*ierr = MatInterpolateAdd(
	(Mat)PetscToPointer((A) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ),
	(Vec)PetscToPointer((w) ));
}
PETSC_EXTERN void  matinterpolate_(Mat A,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = MatInterpolate(
	(Mat)PetscToPointer((A) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  matrestrict_(Mat A,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = MatRestrict(
	(Mat)PetscToPointer((A) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  matmatinterpolateadd_(Mat A,Mat x,Mat w,Mat *y, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(w);
PetscBool y_null = !*(void**) y ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(y);
*ierr = MatMatInterpolateAdd(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((x) ),
	(Mat)PetscToPointer((w) ),y);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! y_null && !*(void**) y) * (void **) y = (void *)-2;
}
PETSC_EXTERN void  matmatinterpolate_(Mat A,Mat x,Mat *y, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(x);
PetscBool y_null = !*(void**) y ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(y);
*ierr = MatMatInterpolate(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((x) ),y);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! y_null && !*(void**) y) * (void **) y = (void *)-2;
}
PETSC_EXTERN void  matmatrestrict_(Mat A,Mat x,Mat *y, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(x);
PetscBool y_null = !*(void**) y ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(y);
*ierr = MatMatRestrict(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((x) ),y);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! y_null && !*(void**) y) * (void **) y = (void *)-2;
}
PETSC_EXTERN void  matgetnullspace_(Mat mat,MatNullSpace *nullsp, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool nullsp_null = !*(void**) nullsp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(nullsp);
*ierr = MatGetNullSpace(
	(Mat)PetscToPointer((mat) ),nullsp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! nullsp_null && !*(void**) nullsp) * (void **) nullsp = (void *)-2;
}
PETSC_EXTERN void  matsetnullspace_(Mat mat,MatNullSpace nullsp, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(nullsp);
*ierr = MatSetNullSpace(
	(Mat)PetscToPointer((mat) ),
	(MatNullSpace)PetscToPointer((nullsp) ));
}
PETSC_EXTERN void  matgettransposenullspace_(Mat mat,MatNullSpace *nullsp, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool nullsp_null = !*(void**) nullsp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(nullsp);
*ierr = MatGetTransposeNullSpace(
	(Mat)PetscToPointer((mat) ),nullsp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! nullsp_null && !*(void**) nullsp) * (void **) nullsp = (void *)-2;
}
PETSC_EXTERN void  matsettransposenullspace_(Mat mat,MatNullSpace nullsp, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(nullsp);
*ierr = MatSetTransposeNullSpace(
	(Mat)PetscToPointer((mat) ),
	(MatNullSpace)PetscToPointer((nullsp) ));
}
PETSC_EXTERN void  matsetnearnullspace_(Mat mat,MatNullSpace nullsp, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(nullsp);
*ierr = MatSetNearNullSpace(
	(Mat)PetscToPointer((mat) ),
	(MatNullSpace)PetscToPointer((nullsp) ));
}
PETSC_EXTERN void  matgetnearnullspace_(Mat mat,MatNullSpace *nullsp, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool nullsp_null = !*(void**) nullsp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(nullsp);
*ierr = MatGetNearNullSpace(
	(Mat)PetscToPointer((mat) ),nullsp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! nullsp_null && !*(void**) nullsp) * (void **) nullsp = (void *)-2;
}
PETSC_EXTERN void  maticcfactor_(Mat mat,IS row, MatFactorInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(row);
*ierr = MatICCFactor(
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((row) ),info);
}
PETSC_EXTERN void  matdiagonalscalelocal_(Mat mat,Vec diag, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(diag);
*ierr = MatDiagonalScaleLocal(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((diag) ));
}
PETSC_EXTERN void  matgetinertia_(Mat mat,PetscInt *nneg,PetscInt *nzero,PetscInt *npos, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(nneg);
CHKFORTRANNULLINTEGER(nzero);
CHKFORTRANNULLINTEGER(npos);
*ierr = MatGetInertia(
	(Mat)PetscToPointer((mat) ),nneg,nzero,npos);
}
PETSC_EXTERN void  matissymmetric_(Mat A,PetscReal *tol,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatIsSymmetric(
	(Mat)PetscToPointer((A) ),*tol,flg);
}
PETSC_EXTERN void  matishermitian_(Mat A,PetscReal *tol,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatIsHermitian(
	(Mat)PetscToPointer((A) ),*tol,flg);
}
PETSC_EXTERN void  matissymmetricknown_(Mat A,PetscBool *set,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatIsSymmetricKnown(
	(Mat)PetscToPointer((A) ),set,flg);
}
PETSC_EXTERN void  matisspdknown_(Mat A,PetscBool *set,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatIsSPDKnown(
	(Mat)PetscToPointer((A) ),set,flg);
}
PETSC_EXTERN void  matishermitianknown_(Mat A,PetscBool *set,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatIsHermitianKnown(
	(Mat)PetscToPointer((A) ),set,flg);
}
PETSC_EXTERN void  matisstructurallysymmetric_(Mat A,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatIsStructurallySymmetric(
	(Mat)PetscToPointer((A) ),flg);
}
PETSC_EXTERN void  matisstructurallysymmetricknown_(Mat A,PetscBool *set,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatIsStructurallySymmetricKnown(
	(Mat)PetscToPointer((A) ),set,flg);
}
PETSC_EXTERN void  matstashgetinfo_(Mat mat,PetscInt *nstash,PetscInt *reallocs,PetscInt *bnstash,PetscInt *breallocs, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(nstash);
CHKFORTRANNULLINTEGER(reallocs);
CHKFORTRANNULLINTEGER(bnstash);
CHKFORTRANNULLINTEGER(breallocs);
*ierr = MatStashGetInfo(
	(Mat)PetscToPointer((mat) ),nstash,reallocs,bnstash,breallocs);
}
PETSC_EXTERN void  matcreatevecs_(Mat mat,Vec *right,Vec *left, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool right_null = !*(void**) right ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(right);
PetscBool left_null = !*(void**) left ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(left);
*ierr = MatCreateVecs(
	(Mat)PetscToPointer((mat) ),right,left);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! right_null && !*(void**) right) * (void **) right = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! left_null && !*(void**) left) * (void **) left = (void *)-2;
}
PETSC_EXTERN void  matfactorinfoinitialize_(MatFactorInfo *info, int *ierr)
{
*ierr = MatFactorInfoInitialize(info);
}
PETSC_EXTERN void  matfactorsetschuris_(Mat mat,IS is, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(is);
*ierr = MatFactorSetSchurIS(
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((is) ));
}
PETSC_EXTERN void  matfactorcreateschurcomplement_(Mat F,Mat *S,MatFactorSchurStatus *status, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
PetscBool S_null = !*(void**) S ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(S);
*ierr = MatFactorCreateSchurComplement(
	(Mat)PetscToPointer((F) ),S,status);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! S_null && !*(void**) S) * (void **) S = (void *)-2;
}
PETSC_EXTERN void  matfactorgetschurcomplement_(Mat F,Mat *S,MatFactorSchurStatus *status, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
PetscBool S_null = !*(void**) S ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(S);
*ierr = MatFactorGetSchurComplement(
	(Mat)PetscToPointer((F) ),S,status);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! S_null && !*(void**) S) * (void **) S = (void *)-2;
}
PETSC_EXTERN void  matfactorrestoreschurcomplement_(Mat F,Mat *S,MatFactorSchurStatus *status, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
PetscBool S_null = !*(void**) S ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(S);
*ierr = MatFactorRestoreSchurComplement(
	(Mat)PetscToPointer((F) ),S,*status);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! S_null && !*(void**) S) * (void **) S = (void *)-2;
}
PETSC_EXTERN void  matfactorsolveschurcomplementtranspose_(Mat F,Vec rhs,Vec sol, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
CHKFORTRANNULLOBJECT(rhs);
CHKFORTRANNULLOBJECT(sol);
*ierr = MatFactorSolveSchurComplementTranspose(
	(Mat)PetscToPointer((F) ),
	(Vec)PetscToPointer((rhs) ),
	(Vec)PetscToPointer((sol) ));
}
PETSC_EXTERN void  matfactorsolveschurcomplement_(Mat F,Vec rhs,Vec sol, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
CHKFORTRANNULLOBJECT(rhs);
CHKFORTRANNULLOBJECT(sol);
*ierr = MatFactorSolveSchurComplement(
	(Mat)PetscToPointer((F) ),
	(Vec)PetscToPointer((rhs) ),
	(Vec)PetscToPointer((sol) ));
}
PETSC_EXTERN void  matfactorinvertschurcomplement_(Mat F, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatFactorInvertSchurComplement(
	(Mat)PetscToPointer((F) ));
}
PETSC_EXTERN void  matfactorfactorizeschurcomplement_(Mat F, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatFactorFactorizeSchurComplement(
	(Mat)PetscToPointer((F) ));
}
PETSC_EXTERN void  matptap_(Mat A,Mat P,MatReuse *scall,PetscReal *fill,Mat *C, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(P);
PetscBool C_null = !*(void**) C ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(C);
*ierr = MatPtAP(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((P) ),*scall,*fill,C);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! C_null && !*(void**) C) * (void **) C = (void *)-2;
}
PETSC_EXTERN void  matrart_(Mat A,Mat R,MatReuse *scall,PetscReal *fill,Mat *C, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(R);
PetscBool C_null = !*(void**) C ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(C);
*ierr = MatRARt(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((R) ),*scall,*fill,C);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! C_null && !*(void**) C) * (void **) C = (void *)-2;
}
PETSC_EXTERN void  matmatmult_(Mat A,Mat B,MatReuse *scall,PetscReal *fill,Mat *C, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
PetscBool C_null = !*(void**) C ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(C);
*ierr = MatMatMult(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ),*scall,*fill,C);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! C_null && !*(void**) C) * (void **) C = (void *)-2;
}
PETSC_EXTERN void  matmattransposemult_(Mat A,Mat B,MatReuse *scall,PetscReal *fill,Mat *C, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
PetscBool C_null = !*(void**) C ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(C);
*ierr = MatMatTransposeMult(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ),*scall,*fill,C);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! C_null && !*(void**) C) * (void **) C = (void *)-2;
}
PETSC_EXTERN void  mattransposematmult_(Mat A,Mat B,MatReuse *scall,PetscReal *fill,Mat *C, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
PetscBool C_null = !*(void**) C ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(C);
*ierr = MatTransposeMatMult(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ),*scall,*fill,C);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! C_null && !*(void**) C) * (void **) C = (void *)-2;
}
PETSC_EXTERN void  matmatmatmult_(Mat A,Mat B,Mat C,MatReuse *scall,PetscReal *fill,Mat *D, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLOBJECT(C);
PetscBool D_null = !*(void**) D ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(D);
*ierr = MatMatMatMult(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ),
	(Mat)PetscToPointer((C) ),*scall,*fill,D);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! D_null && !*(void**) D) * (void **) D = (void *)-2;
}
PETSC_EXTERN void  matcreateredundantmatrix_(Mat mat,PetscInt *nsubcomm,MPI_Fint * subcomm,MatReuse *reuse,Mat *matredundant, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool matredundant_null = !*(void**) matredundant ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(matredundant);
*ierr = MatCreateRedundantMatrix(
	(Mat)PetscToPointer((mat) ),*nsubcomm,
	MPI_Comm_f2c(*(subcomm)),*reuse,matredundant);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! matredundant_null && !*(void**) matredundant) * (void **) matredundant = (void *)-2;
}
PETSC_EXTERN void  matgetlocalsubmatrix_(Mat mat,IS isrow,IS iscol,Mat *submat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(isrow);
CHKFORTRANNULLOBJECT(iscol);
PetscBool submat_null = !*(void**) submat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(submat);
*ierr = MatGetLocalSubMatrix(
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((isrow) ),
	(IS)PetscToPointer((iscol) ),submat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! submat_null && !*(void**) submat) * (void **) submat = (void *)-2;
}
PETSC_EXTERN void  matrestorelocalsubmatrix_(Mat mat,IS isrow,IS iscol,Mat *submat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(isrow);
CHKFORTRANNULLOBJECT(iscol);
PetscBool submat_null = !*(void**) submat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(submat);
*ierr = MatRestoreLocalSubMatrix(
	(Mat)PetscToPointer((mat) ),
	(IS)PetscToPointer((isrow) ),
	(IS)PetscToPointer((iscol) ),submat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! submat_null && !*(void**) submat) * (void **) submat = (void *)-2;
}
PETSC_EXTERN void  matfindzerodiagonals_(Mat mat,IS *is, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
*ierr = MatFindZeroDiagonals(
	(Mat)PetscToPointer((mat) ),is);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
PETSC_EXTERN void  matfindoffblockdiagonalentries_(Mat mat,IS *is, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
*ierr = MatFindOffBlockDiagonalEntries(
	(Mat)PetscToPointer((mat) ),is);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
PETSC_EXTERN void  matinvertvariableblockdiagonal_(Mat mat,PetscInt *nblocks, PetscInt bsizes[],PetscScalar values[], int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(bsizes);
CHKFORTRANNULLSCALAR(values);
*ierr = MatInvertVariableBlockDiagonal(
	(Mat)PetscToPointer((mat) ),*nblocks,bsizes,values);
}
PETSC_EXTERN void  matinvertblockdiagonalmat_(Mat A,Mat C, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(C);
*ierr = MatInvertBlockDiagonalMat(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((C) ));
}
PETSC_EXTERN void  mattransposecoloringdestroy_(MatTransposeColoring *c, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(c);
 PetscBool c_null = !*(void**) c ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(c);
*ierr = MatTransposeColoringDestroy(c);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! c_null && !*(void**) c) * (void **) c = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(c);
 }
PETSC_EXTERN void  mattranscoloringapplysptoden_(MatTransposeColoring coloring,Mat B,Mat Btdense, int *ierr)
{
CHKFORTRANNULLOBJECT(coloring);
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLOBJECT(Btdense);
*ierr = MatTransColoringApplySpToDen(
	(MatTransposeColoring)PetscToPointer((coloring) ),
	(Mat)PetscToPointer((B) ),
	(Mat)PetscToPointer((Btdense) ));
}
PETSC_EXTERN void  mattranscoloringapplydentosp_(MatTransposeColoring matcoloring,Mat Cden,Mat Csp, int *ierr)
{
CHKFORTRANNULLOBJECT(matcoloring);
CHKFORTRANNULLOBJECT(Cden);
CHKFORTRANNULLOBJECT(Csp);
*ierr = MatTransColoringApplyDenToSp(
	(MatTransposeColoring)PetscToPointer((matcoloring) ),
	(Mat)PetscToPointer((Cden) ),
	(Mat)PetscToPointer((Csp) ));
}
PETSC_EXTERN void  mattransposecoloringcreate_(Mat mat,ISColoring iscoloring,MatTransposeColoring *color, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(iscoloring);
PetscBool color_null = !*(void**) color ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(color);
*ierr = MatTransposeColoringCreate(
	(Mat)PetscToPointer((mat) ),
	(ISColoring)PetscToPointer((iscoloring) ),color);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! color_null && !*(void**) color) * (void **) color = (void *)-2;
}
PETSC_EXTERN void  matgetnonzerostate_(Mat mat,PetscObjectState *state, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatGetNonzeroState(
	(Mat)PetscToPointer((mat) ),
	(PetscObjectState* )PetscToPointer((state) ));
}
PETSC_EXTERN void  matcreatempimatconcatenateseqmat_(MPI_Fint * comm,Mat seqmat,PetscInt *n,MatReuse *reuse,Mat *mpimat, int *ierr)
{
CHKFORTRANNULLOBJECT(seqmat);
PetscBool mpimat_null = !*(void**) mpimat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mpimat);
*ierr = MatCreateMPIMatConcatenateSeqMat(
	MPI_Comm_f2c(*(comm)),
	(Mat)PetscToPointer((seqmat) ),*n,*reuse,mpimat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mpimat_null && !*(void**) mpimat) * (void **) mpimat = (void *)-2;
}
PETSC_EXTERN void  matsubdomainscreatecoalesce_(Mat A,PetscInt *N,PetscInt *n,IS *iss[], int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLINTEGER(n);
CHKFORTRANNULLOBJECT(iss);
*ierr = MatSubdomainsCreateCoalesce(
	(Mat)PetscToPointer((A) ),*N,n,iss);
}
PETSC_EXTERN void  matgalerkin_(Mat restrct,Mat dA,Mat interpolate,MatReuse *reuse,PetscReal *fill,Mat *A, int *ierr)
{
CHKFORTRANNULLOBJECT(restrct);
CHKFORTRANNULLOBJECT(dA);
CHKFORTRANNULLOBJECT(interpolate);
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
*ierr = MatGalerkin(
	(Mat)PetscToPointer((restrct) ),
	(Mat)PetscToPointer((dA) ),
	(Mat)PetscToPointer((interpolate) ),*reuse,*fill,A);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
}
PETSC_EXTERN void  mathasoperation_(Mat mat,MatOperation *op,PetscBool *has, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatHasOperation(
	(Mat)PetscToPointer((mat) ),*op,has);
}
PETSC_EXTERN void  mathascongruentlayouts_(Mat mat,PetscBool *cong, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatHasCongruentLayouts(
	(Mat)PetscToPointer((mat) ),cong);
}
PETSC_EXTERN void  matcreategraph_(Mat A,PetscBool *sym,PetscBool *scale,PetscReal *filter,PetscInt *num_idx,PetscInt index[],Mat *graph, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLINTEGER(index);
PetscBool graph_null = !*(void**) graph ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(graph);
*ierr = MatCreateGraph(
	(Mat)PetscToPointer((A) ),*sym,*scale,*filter,*num_idx,index,graph);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! graph_null && !*(void**) graph) * (void **) graph = (void *)-2;
}
PETSC_EXTERN void  mateliminatezeros_(Mat A,PetscBool *keep, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatEliminateZeros(
	(Mat)PetscToPointer((A) ),*keep);
}
#if defined(__cplusplus)
}
#endif
