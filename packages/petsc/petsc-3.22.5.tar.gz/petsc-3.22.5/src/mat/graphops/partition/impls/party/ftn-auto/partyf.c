#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* party.c */
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
#define matpartitioningpartysetglobal_ MATPARTITIONINGPARTYSETGLOBAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningpartysetglobal_ matpartitioningpartysetglobal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningpartysetlocal_ MATPARTITIONINGPARTYSETLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningpartysetlocal_ matpartitioningpartysetlocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningpartysetcoarselevel_ MATPARTITIONINGPARTYSETCOARSELEVEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningpartysetcoarselevel_ matpartitioningpartysetcoarselevel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningpartysetmatchoptimization_ MATPARTITIONINGPARTYSETMATCHOPTIMIZATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningpartysetmatchoptimization_ matpartitioningpartysetmatchoptimization
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningpartysetbipart_ MATPARTITIONINGPARTYSETBIPART
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningpartysetbipart_ matpartitioningpartysetbipart
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matpartitioningpartysetglobal_(MatPartitioning part, char *global, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(part);
/* insert Fortran-to-C conversion for global */
  FIXCHAR(global,cl0,_cltmp0);
*ierr = MatPartitioningPartySetGlobal(
	(MatPartitioning)PetscToPointer((part) ),_cltmp0);
  FREECHAR(global,_cltmp0);
}
PETSC_EXTERN void  matpartitioningpartysetlocal_(MatPartitioning part, char *local, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(part);
/* insert Fortran-to-C conversion for local */
  FIXCHAR(local,cl0,_cltmp0);
*ierr = MatPartitioningPartySetLocal(
	(MatPartitioning)PetscToPointer((part) ),_cltmp0);
  FREECHAR(local,_cltmp0);
}
PETSC_EXTERN void  matpartitioningpartysetcoarselevel_(MatPartitioning part,PetscReal *level, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
*ierr = MatPartitioningPartySetCoarseLevel(
	(MatPartitioning)PetscToPointer((part) ),*level);
}
PETSC_EXTERN void  matpartitioningpartysetmatchoptimization_(MatPartitioning part,PetscBool *opt, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
*ierr = MatPartitioningPartySetMatchOptimization(
	(MatPartitioning)PetscToPointer((part) ),*opt);
}
PETSC_EXTERN void  matpartitioningpartysetbipart_(MatPartitioning part,PetscBool *bp, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
*ierr = MatPartitioningPartySetBipart(
	(MatPartitioning)PetscToPointer((part) ),*bp);
}
#if defined(__cplusplus)
}
#endif
