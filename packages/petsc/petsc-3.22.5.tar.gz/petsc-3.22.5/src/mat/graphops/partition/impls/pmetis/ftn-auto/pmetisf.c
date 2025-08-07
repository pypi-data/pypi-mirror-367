#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* pmetis.c */
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
#define matpartitioningparmetissetcoarsesequential_ MATPARTITIONINGPARMETISSETCOARSESEQUENTIAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningparmetissetcoarsesequential_ matpartitioningparmetissetcoarsesequential
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningparmetissetrepartition_ MATPARTITIONINGPARMETISSETREPARTITION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningparmetissetrepartition_ matpartitioningparmetissetrepartition
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningparmetisgetedgecut_ MATPARTITIONINGPARMETISGETEDGECUT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningparmetisgetedgecut_ matpartitioningparmetisgetedgecut
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmeshtocellgraph_ MATMESHTOCELLGRAPH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmeshtocellgraph_ matmeshtocellgraph
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matpartitioningparmetissetcoarsesequential_(MatPartitioning part, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
*ierr = MatPartitioningParmetisSetCoarseSequential(
	(MatPartitioning)PetscToPointer((part) ));
}
PETSC_EXTERN void  matpartitioningparmetissetrepartition_(MatPartitioning part, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
*ierr = MatPartitioningParmetisSetRepartition(
	(MatPartitioning)PetscToPointer((part) ));
}
PETSC_EXTERN void  matpartitioningparmetisgetedgecut_(MatPartitioning part,PetscInt *cut, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
CHKFORTRANNULLINTEGER(cut);
*ierr = MatPartitioningParmetisGetEdgeCut(
	(MatPartitioning)PetscToPointer((part) ),cut);
}
PETSC_EXTERN void  matmeshtocellgraph_(Mat mesh,PetscInt *ncommonnodes,Mat *dual, int *ierr)
{
CHKFORTRANNULLOBJECT(mesh);
PetscBool dual_null = !*(void**) dual ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dual);
*ierr = MatMeshToCellGraph(
	(Mat)PetscToPointer((mesh) ),*ncommonnodes,dual);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dual_null && !*(void**) dual) * (void **) dual = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
