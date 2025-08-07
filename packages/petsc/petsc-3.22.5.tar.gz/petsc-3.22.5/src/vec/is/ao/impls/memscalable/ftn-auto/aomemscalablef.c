#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* aomemscalable.c */
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

#include "petscao.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aocreatememoryscalable_ AOCREATEMEMORYSCALABLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aocreatememoryscalable_ aocreatememoryscalable
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aocreatememoryscalableis_ AOCREATEMEMORYSCALABLEIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aocreatememoryscalableis_ aocreatememoryscalableis
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  aocreatememoryscalable_(MPI_Fint * comm,PetscInt *napp, PetscInt myapp[], PetscInt mypetsc[],AO *aoout, int *ierr)
{
CHKFORTRANNULLINTEGER(myapp);
CHKFORTRANNULLINTEGER(mypetsc);
PetscBool aoout_null = !*(void**) aoout ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(aoout);
*ierr = AOCreateMemoryScalable(
	MPI_Comm_f2c(*(comm)),*napp,myapp,mypetsc,aoout);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! aoout_null && !*(void**) aoout) * (void **) aoout = (void *)-2;
}
PETSC_EXTERN void  aocreatememoryscalableis_(IS isapp,IS ispetsc,AO *aoout, int *ierr)
{
CHKFORTRANNULLOBJECT(isapp);
CHKFORTRANNULLOBJECT(ispetsc);
PetscBool aoout_null = !*(void**) aoout ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(aoout);
*ierr = AOCreateMemoryScalableIS(
	(IS)PetscToPointer((isapp) ),
	(IS)PetscToPointer((ispetsc) ),aoout);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! aoout_null && !*(void**) aoout) * (void **) aoout = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
